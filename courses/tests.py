from django.test import SimpleTestCase

from alumed.url_utils import build_video_source


class VideoSourceTests(SimpleTestCase):
    def test_detects_youtube_watch_url(self):
        source = build_video_source("https://www.youtube.com/watch?v=abc123", "auto")

        self.assertEqual(source["provider"], "youtube")
        self.assertEqual(source["player"], "videojs")
        self.assertEqual(source["mime_type"], "video/youtube")
        self.assertEqual(source["url"], "https://www.youtube.com/watch?v=abc123")

    def test_detects_google_drive_file_url(self):
        source = build_video_source("https://drive.google.com/file/d/file123/view", "auto")

        self.assertEqual(source["provider"], "google_drive")
        self.assertEqual(source["player"], "iframe")
        self.assertEqual(source["url"], "https://drive.google.com/file/d/file123/preview")

    def test_preserves_google_cloud_signed_query(self):
        source = build_video_source(
            "https://storage.googleapis.com/alumed-storage-br/aula.mp4?X-Goog-Signature=a%2Fb",
            "google_cloud",
        )

        self.assertEqual(source["provider"], "google_cloud")
        self.assertEqual(source["mime_type"], "video/mp4")
        self.assertTrue(source["url"].endswith("?X-Goog-Signature=a%2Fb"))
