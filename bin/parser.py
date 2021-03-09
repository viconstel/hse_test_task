from werkzeug.datastructures import FileStorage
from flask_restplus.reqparse import RequestParser


def setup_parser(parser: RequestParser) -> RequestParser:
    """
    Setup request arguments parser.

    :param parser: app arguments parser
    :return: customized parser
    """
    parser.add_argument('file', location='files', type=FileStorage,
                        required=True, dest='file',
                        help='File to upload into the database.')

    parser.add_argument('--col', action='split', dest='col_names',
                        help='List of new column names in correct order '
                             'as a comma-separated string. The number '
                             'of names must match the number of columns '
                             'in the existing file.')

    parser.add_argument('--head', type=int, dest='header',
                        help='Row number to use as the column names (header).')

    parser.add_argument('--index', action='split', dest='index',
                        help='List of column names to set index on it '
                             '(as a comma-separated string).')

    parser.add_argument('--type', type=eval, dest='type',
                        help='Set data type to the column(s). Argument is '
                             'a dictionary {\'column name\': \'type\'}. '
                             'Available types: int, float, str, datetime.')

    return parser
