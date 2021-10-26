from dotenv import load_dotenv
import os


class DotenvConfig:
    _is_dotenv_read = False

    @property
    def is_dotenv_read(self):
        return self._is_dotenv_read

    def fetch(self, env_key: str):
        if not self.is_dotenv_read:
            self._read_dotenv()
        return os.environ.get(env_key)

    def _read_dotenv(self):
        assert not self.is_dotenv_read, '.env file has already been read'

        loaded_successfully = load_dotenv()
        assert loaded_successfully, 'Failed to load .env'

        self.is_dotenv_read = True
