from src.deploy_tool.macros import Macros


class TestLogger():
    """
    Test macros
    """

    def test_replace(self) -> None:
        """ Test: Add message to log """

        str = '{{test_var1}} and {{test_var2}}'
        d = {
            'test_var1': 'var1',
            'test_var2': 'var2',
        }
        assert Macros.replace(str, d) == 'var1 and var2'
