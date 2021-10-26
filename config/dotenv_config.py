from typing import Dict, Union
from dotenv import dotenv_values


class DotenvConfig:
    """Configuration for environment variables"""
    _config = None

    def __getattr__(self, name: str):
        return self.config[name]

    @property
    def config(self):
        if self._config is None:
            self._config = {
                **dotenv_values()
            }
            self._validate_args()
        return self._config

    def _validate_args(self):
        pass
