from pathlib import Path
import uuid 
import shutil


def save_video(video , uploads_dir : str) : 

    # create a unique id for the video
    video_id =uuid.uuid4().hex[:8]

    # build the file extension
    file_extension = Path(video.filename).suffix

    # build the filename
    stored_filename = f'uploaded_video_{video_id}{file_extension}'

    # build the storage path
    stored_path = Path(uploads_dir) / stored_filename

    stored_path.parent.mkdir(parents=True, exist_ok=True)

    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    
    return stored_path

    
    
