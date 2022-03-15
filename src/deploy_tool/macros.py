class Macros:
    """
    Deploy tool macros replacer
    """

    def replace(text: str, dictionary: dict) -> str:
        """
        Replace macroses in string
        Example: {{macros}} => macros_value
        """

        for macros in dictionary:
            text = text.replace(
                ''.join(['{{', macros,  '}}']),
                dictionary[macros]
            )

        return text
