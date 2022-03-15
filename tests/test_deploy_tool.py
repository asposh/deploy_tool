from src.deploy_tool.db_postgres import DbPostgres
from src.deploy_tool.deploy_tool import DeployTool
from src.deploy_tool.macros import Macros
import argparse
import pytest
import os


class TestDeployTool():
    """
    Test DeployTool
    """

    def setup(self):
        self.options = self.__get_options()
        self.options_available = self.options.keys()
        params = {
            'options': self.options,
            'options_available': self.options_available,
        }
        self.deploy_tool = DeployTool(params)

    def __get_options(self) -> dict:
        """ Get DeployTool options """

        return {
            'db_type': 'test_db_type',
            'db_name': 'test_name',
            'db_host': 'test_host',
            'db_port': 'test_port',
            'db_user': 'test_user',
            'db_password': 'test_db_password',
            'mount_dir': 'test_mount_dir',
        }

    def test_init_db(self, mocker) -> None:
        """ Test DB initialisation """

        deploy_tool = self.deploy_tool
        options = self.options

        # Unknown DB type
        with pytest.raises(ValueError) as exc_info:
            deploy_tool.init_db()
        assert f'Unknown DB type: {options["db_type"]}' in str(exc_info.value)

        # PostgreSQL type ('pgsql')
        deploy_tool.options['db_type'] = 'pgsql'
        mocker.patch.object(DbPostgres, 'init_db', side_effect=lambda: 1)
        deploy_tool.init_db()
        assert deploy_tool.db == 1

    def test_query_from_file(self, mocker) -> None:
        """ Test DB query from file """

        deploy_tool = self.deploy_tool

        # Undefined DB
        mocker.patch.object(deploy_tool.logger, 'add', autospec=True)
        deploy_tool.query_from_file()
        deploy_tool.logger.add.assert_called_with(
            'DB isn\'t initialised, use init_db() before'
        )

        # Defined DB
        deploy_tool.db = mocker.Mock()
        deploy_tool.db.query_from_file = mocker.Mock()
        deploy_tool.query_from_file()
        deploy_tool.db.query_from_file.assert_called()

        # Query error
        deploy_tool.db.query_from_file = lambda x: 0/0
        deploy_tool.query_from_file()
        deploy_tool.logger.add.assert_called_with(
            'Can\'t execute query: division by zero'
        )

    def test_build_config(self, mocker) -> None:
        """ Build config file """

        src = 'src'
        dest = 'dst'
        deploy_tool = self.deploy_tool

        def macros_replace_mock(*args, **kwargs):
            return src if args[0] == src else dest

        mocker.patch.object(deploy_tool.logger, 'add', autospec=True)
        mocker.patch.object(
            Macros,
            'replace',
            autospec=True,
            side_effect=macros_replace_mock
        )
        mocker.patch.object(
            deploy_tool,
            '_DeployTool__make_config_file',
            autospec=True
        )

        # Success build
        deploy_tool.build_config(src, dest)
        deploy_tool.logger.add.assert_called_with(f'Build file: {dest}')
        Macros.replace.assert_any_call(src, deploy_tool.options)
        Macros.replace.assert_any_call(dest, deploy_tool.options)
        deploy_tool._DeployTool__make_config_file.assert_called_with(src, dest)

        # Fail build
        deploy_tool._DeployTool__make_config_file = lambda x, y: 0/0
        deploy_tool.build_config(src, dest)
        deploy_tool.logger.add.assert_called_with(
            f'Can\'t build config {dest}: division by zero'
        )

    def test_init_options(self) -> None:
        """ Test options initialisation """

        options = {
            'test_option1': 1,
            'test_option2': 2,
        },
        options_available = {
            'test_available_option1': 1,
            'test_available_option2': 2,
        },
        params = {
            'options': options,
            'options_available': options_available,
        }

        deploy_tool = DeployTool(params)
        assert deploy_tool.options == options
        assert deploy_tool.options_available == options_available

    def test_get_options(self, mocker) -> None:
        """ Test get options """

        deploy_tool = self.deploy_tool
        options = self.options

        mocker.patch(
            'argparse.ArgumentParser',
            side_effect=lambda: ArgumentParserMock()
        )
        mocker.patch.object(
            deploy_tool,
            '_DeployTool__options_to_dict',
            side_effect=lambda x: x
        )

        # Predefined options
        test_options = deploy_tool._DeployTool__get_options()
        assert options == test_options

        # Parse options
        deploy_tool.options = None
        test_options = deploy_tool._DeployTool__get_options()

        options = {}
        for option in self.options_available:
            options['--' + option] = True

        assert options == test_options

    def test_options_to_dict(self) -> None:
        """ Test options to dict """

        deploy_tool = self.deploy_tool
        options = self.options

        args = argparse.Namespace()
        for option in options:
            setattr(args, option, options[option])

        test_options = deploy_tool._DeployTool__options_to_dict(args)
        assert options == test_options

    def test_make_config_file(self, mocker) -> None:
        """ Test make config file """

        src = 'src'
        dest = 'dst'
        src_data = 'source_data'
        deploy_tool = self.deploy_tool

        mocker.patch('os.path.dirname', return_value=dest)
        mocker.patch('os.makedirs', autospec=True)
        mocker.patch('builtins.open', mocker.mock_open(read_data=src_data))
        mocker.patch.object(
            Macros,
            'replace',
            autospec=True,
            return_value=src_data
        )

        deploy_tool._DeployTool__make_config_file(src, dest)
        Macros.replace.assert_called_with(src_data, deploy_tool.options)
        os.path.dirname.assert_called_with(dest)
        os.makedirs.assert_called_with(dest, exist_ok=True)
        open.assert_any_call(src, encoding=deploy_tool.ENCODING)
        open.assert_any_call(dest, 'w', encoding=deploy_tool.ENCODING)


class ArgumentParserMock():
    """ ArgumentParser mock """

    def __init__(self):
        self.args = {}

    def add_argument(self, arg):
        """ Add argument """

        self.args[arg] = True

    def parse_args(self):
        """ Parse arguments """

        return self.args
