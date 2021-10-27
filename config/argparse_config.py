from argparse import ArgumentParser, Namespace


class ArgparseConfig:
    """Configuration for command line arguments"""
    _args: Namespace = None
    _parser: ArgumentParser = None

    def __contains__(self, key: str) -> bool:
        return key in self.args

    def __getitem__(self, key: str):
        if key not in self.args:
            raise KeyError(f'ArgparseConfig has no item \'{key}\'')
        return getattr(self.args, key)

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
        parser.add_argument('--img', help='File path to test image')
        parser.add_argument('-a', '--annotations', help='File path to annotation JSON')
