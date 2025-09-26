import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

PROCESSED_VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/videos/processed'))

def test_list_processed_videos():
    response = client.get("/pipeline/processed-videos")
    assert response.status_code == 200
    files = response.json()
    assert isinstance(files, list)
    # Check that at least one known file is present (if any exist)
    if os.listdir(PROCESSED_VIDEOS_DIR):
        for f in os.listdir(PROCESSED_VIDEOS_DIR):
            assert f in files

def test_download_processed_video():
    files = os.listdir(PROCESSED_VIDEOS_DIR)
    if not files:
        pytest.skip("No processed videos to test download.")
    filename = files[0]
    response = client.get(f"/pipeline/processed-videos/{filename}")
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment;")
    assert response.content  # File should not be empty
