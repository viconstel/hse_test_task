"""
A microservice that processes .xlsx or .csv files
and loads them into a PostgreSQL database.
"""


import os
from typing import Union

import pandas as pd
from flask import Flask, render_template, make_response, flash, redirect
from flask_restplus import Api, Resource
from flask_restplus.reqparse import ParseResult
from sqlalchemy.exc import SQLAlchemyError, OperationalError, ProgrammingError
from dateutil.parser import ParserError

from .parser import setup_parser
from .database import DataBase
from .utils import is_date


JSON_HEADER = {'Content-Type': 'application/json'}
HTML_HEADER = {'Content-Type': 'text/html'}


# App settings
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.xlsx', '.csv']
app.secret_key = '12345'

api = Api(app=app,
          version="1.0",
          title="XLSX/CSV files processing service",
          description="This service process XLSX/CSV files "
                      "and store it to the PostgreSQL database."
          )
upload_ns = api.namespace('upload', description='Upload name space.')
upload_parser = setup_parser(upload_ns.parser())


@upload_ns.route('/')
class UploadDemo(Resource):

    """Class that provides GET and POST methods to process input files."""

    @upload_ns.produces(['text/html'])
    @upload_ns.response(200, 'Success')
    def get(self):
        """GET method that renders home page."""
        response = make_response(render_template('home_page.html'), 200,
                                 HTML_HEADER)

        return response

    @upload_ns.expect(upload_parser)
    @upload_ns.produces(['text/html', 'application/json'])
    @upload_ns.response(200, 'Success', headers=HTML_HEADER)
    @upload_ns.response(422, 'Error while processing data', headers=JSON_HEADER)
    @upload_ns.response(500, 'Internal Server Error', headers=JSON_HEADER)
    def post(self):
        """POST method to upload file and put it into database."""
        # Parse request arguments
        args = upload_parser.parse_args()
        file = args.get('file')
        file_ext = os.path.splitext(file.filename)[1]

        # Check file format
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            upload_ns.abort(422, 'Wrong file format')

        # Parse file data into the Pandas Dataframe
        try:
            header = args.get('header')
            if header is None and file_ext == '.csv':
                header = 0

            if file_ext == '.csv':
                dataframe = pd.read_csv(file, header=header)
            elif file_ext == '.xlsx':
                dataframe = pd.read_excel(file, header=header)
        except (ValueError, pd.errors.ParserError):
            upload_ns.abort(422, 'Unable to parse data')

        # Data preprocessing before loading into the database
        dataframe = preprocess_dataframe(dataframe, args)
        if isinstance(dataframe, str):
            upload_ns.abort(422, dataframe)

        # Connect to the PostgreSQL database
        db = DataBase()
        table_name = file.filename.replace('.', '_')
        try:
            # Load table for the first time
            if table_name not in db.engine.table_names():
                dataframe.to_sql(table_name, con=db.engine)
                db.set_primary_key(table_name)
            # Inserting data in the existing table
            else:
                max_index = db.get_max_index(table_name)
                if max_index is not None:
                    dataframe.index += max_index
                dataframe.to_sql(table_name, con=db.engine, if_exists='append')

            # Set index on the specified columns
            col_index = args.get('index')
            if col_index is not None:
                col_index = [col.strip() for col in col_index]
                db.set_index_on_columns(table_name, col_index)

        except OperationalError:
            upload_ns.abort(500, 'Error connecting to database')
        except ProgrammingError:
            upload_ns.abort(500, 'Database query error')
        except SQLAlchemyError:
            upload_ns.abort(500, 'Database error')
        finally:
            db.engine.dispose()

        # Temporary message
        flash(f'File {file.filename} uploaded successfully, select new one!')

        return redirect(upload_ns.path)


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse dates in the dataframe columns if it is possible.

    :param df: dataframe for processing
    :return: dataframe with parsed dates
    """
    for col_name in df.columns:
        if not df[col_name].empty and df[col_name].dtype == 'object':
            if is_date(df[col_name][0]):
                try:
                    df[col_name] = df[col_name].apply(pd.to_datetime)
                except (ParserError, ValueError):
                    pass
    return df


def preprocess_dataframe(df: pd.DataFrame, args: ParseResult) -> Union[str, pd.DataFrame]:
    """
    Preprocess data before loading in the database. Rename specified
    columns and change data type if it was required by request arguments.

    :param df: dataframe for preprocessing
    :param args: request arguments
    :return: dataframe after preprocessing or error message
    """
    df = parse_dates(df)

    # Set new column names
    col_names = args.get('col_names')
    if col_names is not None:
        try:
            col_names = [col.strip() for col in col_names]
            df.columns = col_names
        except ValueError:
            message = f'Wrong argument --col={col_names}'
            return message

    # Change columns data type
    col_type = args.get('type')
    if col_type is not None:
        try:
            for col, typ in col_type.items():
                if typ == 'datetime':
                    typ = 'datetime64[ns]'

                df[col] = df[col].astype(typ)
        except ValueError:
            message = f'Wrong argument --type={col_type}'
            return message

    return df


if __name__ == '__main__':
    app.run()
