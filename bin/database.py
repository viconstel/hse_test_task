from typing import Union

from sqlalchemy import create_engine

from utils import read_config


CONFIG_PATH = '../config/config.yml'
DB_STRING = 'postgres://{user}:{password}@{host}:{port}/{db_name}'


class DataBase:

    """Class for interacting with the PostgreSQL database."""

    def __init__(self) -> None:
        """Class initializer"""
        conf = read_config(CONFIG_PATH)['postgres_db']
        conn_string = DB_STRING.format(user=conf['user'],
                                       password=conf['password'],
                                       host=conf['host'],
                                       port=conf['port'],
                                       db_name=conf['database_name']
                                       )
        # Establish new connection
        self.engine = create_engine(conn_string)

    def set_primary_key(self, table: str) -> None:
        """
        Set primary key on the 'index' column.

        :param table: name of the table to modify
        """
        with self.engine.connect() as con:
            con.execute(f'ALTER TABLE {table} ADD PRIMARY KEY (index);')

    def get_max_index(self, table: str) -> Union[int, None]:
        """
        Get start index for the next insertion.

        :param table: name of the table
        :return: next index or None
        """
        index = None

        if table in self.engine.table_names():
            with self.engine.connect() as con:
                response = con.execute(f'SELECT COUNT(index) FROM {table};')
                index = response.fetchone()[0]

        return index

    def set_index_on_columns(self, table: str, columns: list) -> None:
        """
        Set index on the specified columns in the 'table'.

        :param table: name of the table
        :param columns: the columns to be indexed
        """
        query = 'CREATE INDEX {idx} ON {table}({column});'

        if len(columns) > 0:
            # Index name
            idx_name = '_'.join(columns) + '_idx'
            with self.engine.connect() as con:
                con.execute(query.format(
                    idx=idx_name,
                    table=table,
                    column=', '.join(columns)
                ))
