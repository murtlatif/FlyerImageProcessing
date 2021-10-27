from .argparse_config import ArgparseConfig
from .dotenv_config import DotenvConfig


class Config:
    args: ArgparseConfig = ArgparseConfig()
    env: DotenvConfig = DotenvConfig()
