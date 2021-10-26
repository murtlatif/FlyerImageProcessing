from .dotenv_config import DotenvConfig
from .argparse_config import ArgparseConfig

class Config:
    env: DotenvConfig = DotenvConfig()
    args: ArgparseConfig = ArgparseConfig()
