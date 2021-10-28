from dotenv import dotenv_values


class DotenvConfig:
    """Configuration for environment variables"""
    _config = None

    def __contains__(self, key: str) -> bool:
        return key in self.config

    def __getitem__(self, key: str) -> str:
        if key not in self.config:
            raise KeyError(f'DotenvConfig has no item \'{key}\'')
        return self.config[key]

    def __getattr__(self, name: str) -> str:
        if name not in self.config:
            raise AttributeError(f'DotenvConfig has no attribute \'{name}\'.')

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
