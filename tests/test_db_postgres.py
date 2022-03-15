from src.deploy_tool.db_postgres import DbPostgres
from src.deploy_tool.logger import Logger
from src.deploy_tool.macros import Macros
from copy import deepcopy
import os
import pytest
import psycopg2


class TestDbPostgres():
    """
    Test PostgreSQL DB
    """

    def setup(self):
        options = self.__get_options()
        logger = Logger()
        self.db_postgres = DbPostgres(options, logger)
        self.db_postgres.cursor = CursorMock()
        self.query = 'test_query'
        self.path = 'test_path'

    def __get_options(self) -> dict:
        """ Get DbPostgres options """

        return {
            'db_name': 'test_name',
            'db_host': 'test_host',
            'db_port': 'test_port',
            'db_user': 'test_user',
            'db_password': 'test_db_password',
        }

    def test_default(self):
        """ Test test default values """

        db_postgres = self.db_postgres
        assert db_postgres.DEFAULT_DB_CREATE \
               == "CREATE DATABASE {{db_name}} WITH ENCODING 'UTF8'"
        assert db_postgres.DEFAULT_SQL_FILE \
               == "{{mount_dir}}/deploy/db/dump.sql"

    def test_init_db(self, mocker):
        """ Test DB initialisation """

        db_postgres = self.db_postgres
        mocker.patch.object(db_postgres, '_DbPostgres__check_options')

        # Good connection
        db_postgres_good_connect = deepcopy(db_postgres)
        mocker.patch.object(db_postgres_good_connect, '_DbPostgres__connect')
        init = db_postgres_good_connect.init_db()
        db_postgres_good_connect._DbPostgres__connect.assert_called()
        assert init == db_postgres_good_connect

        # Bad connection
        db_postgres_bad_connect = deepcopy(db_postgres)
        mocker.patch.object(
            db_postgres_bad_connect.logger,
            'add',
            autospec=True
        )
        mocker.patch.object(db_postgres_bad_connect, '_DbPostgres__create')

        db_name = db_postgres_bad_connect.options["db_name"]
        with pytest.raises(psycopg2.OperationalError):
            mocker.patch.object(
                db_postgres_bad_connect,
                '_DbPostgres__connect',
                side_effect=psycopg2.OperationalError()
            )
            init = db_postgres_bad_connect.init_db()
        db_postgres_bad_connect.logger.add.assert_called_with(
            f'Can\'t connect to DB: {db_name}'
        )
        db_postgres_bad_connect._DbPostgres__create.assert_called()
        db_postgres_bad_connect._DbPostgres__connect.assert_called()

    def test_query_from_file(self, mocker) -> None:
        """ Test execute DB query from file """

        db_postgres = self.db_postgres
        path = self.path
        query = self.query

        def macros_replace_mock(*args, **kwargs):
            return query if args[0] == query else path

        # Bad path
        mocker.patch.object(db_postgres.logger, 'add', autospec=True)
        mocker.patch('os.path.isfile', return_value=False)
        mocker.patch.object(Macros, 'replace', side_effect=macros_replace_mock)
        db_postgres.query_from_file(path)

        os.path.isfile.assert_called_with(path)
        Macros.replace.assert_called_with(path, db_postgres.options)
        db_postgres.logger.add.assert_called_with(
            f'Dump file {path} isn\'t exists'
        )

        # Good path
        mocker.patch.object(db_postgres.logger, 'add', autospec=True)
        mocker.patch('os.path.isfile', return_value=True)
        mocker.patch('builtins.open', mocker.mock_open(read_data=query))
        mocker.patch.object(db_postgres.cursor, 'execute', autospec=True)
        db_postgres.query_from_file(path)

        Macros.replace.assert_called_with(query, db_postgres.options)
        db_postgres.logger.add.assert_called_with(
            f'Execute PostgreSQL query from {path}'
        )
        db_postgres.cursor.execute.assert_called_with(query)

        # Default path
        path = db_postgres.DEFAULT_SQL_FILE
        db_postgres.query_from_file()
        open.assert_called_with(path)

    def test_create(self, mocker) -> None:
        """ Test connect """

        query = self.query
        db_postgres = self.db_postgres

        mocker.patch.object(
            Macros,
            'replace',
            autospec=True,
            return_value=query
        )
        mocker.patch.object(db_postgres, '_DbPostgres__connect', autospec=True)
        mocker.patch.object(db_postgres.logger, 'add', autospec=True)
        mocker.patch.object(db_postgres.cursor, 'execute', autospec=True)

        db_postgres._DbPostgres__create(query)
        db_postgres.logger.add.assert_called_with(
            f'Creating new Postgres DB: {db_postgres.options["db_name"]}'
        )
        db_postgres._DbPostgres__connect.assert_called_with(False)
        Macros.replace.assert_called_with(query, db_postgres.options)
        db_postgres.cursor.execute.assert_called_with(query)

        # Default DB create query
        db_postgres._DbPostgres__create()
        Macros.replace.assert_called_with(
            db_postgres.DEFAULT_DB_CREATE, db_postgres.options
        )

    def test_connect(self, mocker) -> None:
        """ Test connect """

        db_postgres = self.db_postgres
        connect_mock = ConnectMock()
        mocker.patch('psycopg2.connect', return_value=connect_mock)

        # Connect without DB
        db_postgres._DbPostgres__connect(False)
        dsn = (
            f'user={db_postgres.options["db_user"]} '
            f'password={db_postgres.options["db_password"]} '
            f'host={db_postgres.options["db_host"]} '
            f'port={db_postgres.options["db_port"]}'
        )
        psycopg2.connect.assert_called_with(dsn)

        # Connect to DB
        db_postgres._DbPostgres__connect(True)
        dsn += f' dbname={db_postgres.options["db_name"]}'
        psycopg2.connect.assert_called_with(dsn)

        assert db_postgres.cursor == 'test_cursor'
        assert db_postgres.connection == connect_mock
        assert db_postgres.connection.autocommit is True

    def test_check_options(self) -> None:
        """ Test check options """

        db_postgres = self.db_postgres
        del db_postgres.options['db_password']

        with pytest.raises(NameError) as exc_info:
            db_postgres._DbPostgres__check_options()

        assert 'db_password undefined' in str(exc_info.value)


class ConnectMock():
    """ Psycopg2 connect mock """

    def __init__(self):
        self.autocommit = False
        self.cursor = lambda: 'test_cursor'


class CursorMock():
    """ Psycopg2 cursor mock"""

    def execute(self, query):
        """ Psycopg2 cursor mock execute """

        pass
