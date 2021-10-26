from argparse import ArgumentParser, Namespace


class ArgparseConfig:
    """Configuration for command line arguments"""
    _args: Namespace = None
    _parser: ArgumentParser = None

    def __getattr__(self, name: str):
        return getattr(self.args, name)

    @property
    def parser(self):
        if self._parser is None:
            self._parser = ArgumentParser()
            self._add_arguments_to_parser(self._parser)
        return self._parser

    @property
    def args(self):
        if self._args is None:
            self._args = self.parser.parse_args()
            self._validate_args()
        return self._args

    def _validate_args(self):
        pass

    def _add_arguments_to_parser(self, parser: ArgumentParser):
        pass
