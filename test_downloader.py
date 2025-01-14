import unittest
from downloader import Downloader, validate_url, detect_content_type, DownloadError, WatermarkRemovalError
from unittest.mock import patch
import requests

class TestDownloader(unittest.TestCase):

    def test_validate_url(self):
        # Valid URL
        valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        invalid_url = "https://www.unknownsite.com/watch?v=dQw4w9WgXcQ"

        self.assertTrue(validate_url(valid_url))
        with self.assertRaises(ValueError):
            validate_url(invalid_url)

    def test_detect_content_type(self):
        video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        audio_url = "https://www.spotify.com/track/12345"
        unknown_url = "https://www.unknownsite.com/somefile.xyz"

        self.assertEqual(detect_content_type(video_url), "video")
        self.assertEqual(detect_content_type(audio_url), "audio")
        self.assertEqual(detect_content_type(unknown_url), "unknown")

    @patch('yt_dlp.YoutubeDL.download')
    def test_download_video(self, mock_download):
        downloader = Downloader("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_download.return_value = None
        self.assertEqual(downloader.download_video(save_path="test_video.mp4"), "test_video.mp4")

    @patch('requests.get')
    def test_download_file(self, mock_get):
        downloader = Downloader("https://www.example.com/sample.pdf")
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.content = b"sample content"
        mock_get.return_value = mock_response

        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            downloader.download_file("pdf", "test.pdf")
            mock_file.assert_called_once_with("test.pdf", 'wb')

    def test_remove_watermark_inpaint(self):
        downloader = Downloader("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        try:
            downloader.remove_watermark_inpaint("test_video.mp4", "output_video.mp4")
            self.assertTrue(True)  # Success
        except WatermarkRemovalError:
            self.fail("Watermark removal raised an error unexpectedly")

if __name__ == "__main__":
    unittest.main()
