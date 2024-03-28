from pathlib import Path

from mextractor.workflow import mextract_videos_in_subdirs

video_path = Path("/run/media/can/388269cd-66f7-4c8d-822b-bf3cb57b5b9e/backuup/old/Downloads/Compressed/nort")

mextract_videos_in_subdirs(video_path, ".mp4", only_frame=False)
