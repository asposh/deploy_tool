import psycopg2
import os.path
from .logger import Logger
from .macros import Macros


class DbPostgres:
    """
    PostgreSQL DB
    """

    # Default queries
    DEFAULT_DB_CREATE: str = "CREATE DATABASE {{db_name}} WITH ENCODING 'UTF8'"
    DEFAULT_SQL_FILE: str = "{{mount_dir}}/deploy/db/dump.sql"

    def __init__(self, options: dict, logger: Logger):
        self.options = options
        self.logger = logger
        self.connection = None
        self.cursor = None

    def init_db(self) -> psycopg2.extensions.cursor:
        """  PostgreSQL DB initialisation

             If db exists, returns it
             If not, create new db
        """

        self.__check_options()

        try:
            self.__connect()
        except psycopg2.OperationalError:
            # Init new db
            self.logger.add(f'Can\'t connect to DB: {self.options["db_name"]}')

            # Create db
            self.__create()

            # Connect to a new db
            self.__connect()

        return self

    def query_from_file(self, path: str = '') -> None:
        """ Execute PostgreSQL DB query from file """

        if not path:
            path = DbPostgres.DEFAULT_SQL_FILE

        path = Macros.replace(path, self.options)

        if not os.path.isfile(path):
            self.logger.add(f'Dump file {path} isn\'t exists')
            return

        with open(path) as f:
            query = f.read()

        query = Macros.replace(query, self.options)
        self.logger.add(f'Execute PostgreSQL query from {path}')
        self.cursor.execute(query)

    def __create(self, query: str = '') -> None:
        """ Create PostgreSQL DB """

        if not query:
            query = DbPostgres.DEFAULT_DB_CREATE

        self.logger.add(f'Creating new Postgres DB: {self.options["db_name"]}')

        self.__connect(False)
        query = Macros.replace(query, self.options)

        self.cursor.execute(query)

    def __connect(self, to_db: bool = True) -> None:
        """ Connect to PostgreSQL DB """

        dsn = [
            f'user={self.options["db_user"]}',
            f'password={self.options["db_password"]}',
            f'host={self.options["db_host"]}',
            f'port={self.options["db_port"]}',
        ]
        if to_db:
            dsn += [f'dbname={self.options["db_name"]}']

        self.connection = psycopg2.connect(' '.join(dsn))
        self.connection.autocommit = True

        self.cursor = self.connection.cursor()

    def __check_options(self) -> None:
        """ Check options """

        for option in [
            'db_name',
            'db_host',
            'db_port',
            'db_user',
            'db_password',
        ]:
            if option not in self.options or not self.options[option].strip():
                raise NameError(f'{option} undefined')
