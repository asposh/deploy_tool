import argparse
import copy
import os
from typing import Optional
from .db_postgres import DbPostgres
from .logger import Logger
from .macros import Macros


class DeployTool:
    """
    Python deploy tool
    """

    # Default params
    DEFAULT_CLI_OPTIONS: list = [
        'db_type',
        'db_name',
        'db_host',
        'db_port',
        'db_user',
        'db_password',
        'mount_dir',
    ]

    ENCODING: str = 'utf-8'

    def __init__(self, params: Optional[dict] = None):
        self.db = None
        self.logger = Logger()

        # Options initialisation
        self.__init_options(params)

    def init_db(self) -> None:
        """ DB initialisation factory """

        options = self.__get_options()

        try:
            db = self.__db_factory(options)
            self.db = db.init_db()
        except Exception as e:
            self.logger.add('Can\'t initialise DB: ' + str(e))

    def query_from_file(self, path: str = '') -> None:
        """ Execute DB query from file """

        if not self.db:
            self.logger.add('DB isn\'t initialised, use init_db() before')
            return

        try:
            self.db.query_from_file(path)
        except Exception as e:
            self.logger.add('Can\'t execute query: ' + str(e))

    def build_config(self, src: str, dest: str) -> None:
        """ Build config file """

        options = self.__get_options()

        src = Macros.replace(src, options)
        dest = Macros.replace(dest, options)

        self.logger.add(f'Build file: {dest}')

        try:
            self.__make_config_file(src, dest)
        except Exception as e:
            self.logger.add(f'Can\'t build config {dest}: ' + str(e))

    def __db_factory(self, options: dict) -> object:
        """ DB factory """

        if options['db_type'] == 'pgsql':
            return DbPostgres(options, self.logger)

        raise ValueError(f'Unknown DB type: {options["db_type"]}')

    def __init_options(self, params: Optional[dict] = None) -> None:
        """ Options initialisation """

        self.options = {}
        self.options_available = copy.deepcopy(DeployTool.DEFAULT_CLI_OPTIONS)

        if not params:
            return

        if 'options' in params:
            self.options = params['options']

        if 'options_available' in params:
            self.options_available = params['options_available']

    def __get_options(self) -> dict:
        """ Get options """

        if self.options:
            return self.options

        parser = argparse.ArgumentParser()
        for opt in self.options_available:
            parser.add_argument('--' + opt)
        args = parser.parse_args()

        self.options = self.__options_to_dict(args)

        return self.options

    def __options_to_dict(self, args: argparse.Namespace) -> dict:
        """ Build dict from args """

        options = {}
        for opt in self.options_available:
            if hasattr(args, opt):
                options[opt] = getattr(args, opt)

        return options

    def __make_config_file(self, src: str, dest: str) -> None:
        """ Make config file """

        with open(src, encoding=self.ENCODING) as file_src:
            source_content = Macros.replace(file_src.read(), self.options)

            # Create directories
            os.makedirs(os.path.dirname(dest), exist_ok=True)

            with open(dest, 'w', encoding=self.ENCODING) as file_dest:
                file_dest.write(source_content)
