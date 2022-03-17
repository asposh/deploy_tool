from src.deploy_tool.logger import Logger


class TestLogger():
    """
    Test logger
    """

    def test_add(self, capsys) -> None:
        """ Test: Add message to log """

        logger = Logger()

        messsage = 'Test message'
        logger.add(messsage)
        captured = capsys.readouterr()
        assert captured.out == messsage + '1\n'
