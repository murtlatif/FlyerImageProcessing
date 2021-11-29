from argparse import ArgumentParser, Namespace
from util.constants import COMMAND


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
        # can_get_annotations = (self._args.annotations_file is not None) or (
        #     self._args.image_path is not None and self._args.request_ocr)

        # can_show_image = self._args.image_path is not None

        # assert can_get_annotations

        # if self._args.display:
        #     assert can_show_image

        # if self._args.command == COMMAND.SEGMENTATION:
        #     assert self._args.model_state is not None
        pass

    def _add_arguments_to_parser(self, parser: ArgumentParser):
        parser.add_argument('-a', '--annotations-file', help='File path to annotation JSON')
        parser.add_argument('-i', '--image', dest='image_path', help='File path to test image')
        parser.add_argument('-r', '--request-ocr', action='store_true',
                            help='Request annotation from OCR service as a fall back')
        parser.add_argument('-sm', '--segmentation-model-state', help='File path to the segmentation model state dict')
        parser.add_argument('-cm', '--classifier-model-state',
                            help='File path to the product classifier model state dict')
        parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity of program')
        parser.add_argument('--save', action='store_true', help='Add a save modifier to the command')
        parser.add_argument('--display', action='store_true', help='Add a display modifier to the command')
        parser.add_argument('--download', action='store_true', help='Download NLTK data')
