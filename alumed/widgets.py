from django import forms
from google.cloud import storage
from django.conf import settings


class GCSFileSelectWidget(forms.Select):
    def __init__(self, attrs=None, prefix="courses_images/"):
        super().__init__(attrs)
        self.prefix = prefix.rstrip("/") + "/"   # garante a barra
        self.client = storage.Client.from_service_account_json(settings.GS_CREDENTIALS_FILE)
        self.bucket = self.client.bucket(settings.GS_BUCKET_NAME)

    def get_files(self):
        blobs = self.bucket.list_blobs(prefix=self.prefix)
        return [(blob.name, blob.name) for blob in blobs]

    def render(self, name, value, attrs=None, renderer=None):
        self.choices = self.get_files()
        return super().render(name, value, attrs, renderer)
