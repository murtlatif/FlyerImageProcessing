
from config import Config
from google.auth._default import load_credentials_from_file
from google.auth.credentials import Credentials
from google.cloud.vision import (AnnotateImageResponse, Image,
                                 ImageAnnotatorClient)


class GoogleCloudClient:
    _image_annotator_client = None

    @property
    def image_annotator_client(self):
        if self._image_annotator_client is None:
            self._image_annotator_client = ImageAnnotatorClient(credentials=load_google_cloud_credentials())
        return self._image_annotator_client

    def request_text_detection(self, path):
        """
        Requests text detection from Google Cloud on the given image.

        WARNING: This function will make a request to Google Cloud and could
        result in billing charges. Be careful when using this.

        Args:
            path (PathLike): The file path to image to perform text detection on

        Returns:
            AnnotateImageResponse: The resulting annotation response.
        """
        client = self.image_annotator_client

        with open(path, 'rb') as image_file:
            content = image_file.read()

        image = Image(content=content)

        response: AnnotateImageResponse = client.text_detection(image=image)

        return response


def load_google_cloud_credentials() -> Credentials:
    """
    Load the Google Cloud private key located at the GOOGLE_CLOUD_PKEY_PATH
    environment variable into a Google Auth credentials object.

    Returns:
        Credentials: The credentials for Google Auth
    """
    credentials, project_id = load_credentials_from_file(Config.env.GOOGLE_CLOUD_PKEY_PATH)
    print(f'✅ Loaded Google Cloud credentials for project {project_id}.')

    return credentials
