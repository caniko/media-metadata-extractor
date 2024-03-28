import cv2
from pydantic import FilePath, validate_call

from mextractor.base import ImageMextractorMetadata, VideoMextractorMetadata


@validate_call
def extract_image(path_to_image: FilePath, include_image: bool = True) -> ImageMextractorMetadata:
    image = cv2.imread(str(path_to_image))

    return ImageMextractorMetadata(
        name=path_to_image.stem,
        resolution=(image.shape[1], image.shape[0]),
        image=image if include_image else None,
    )


@validate_call
def extract_video_frame(
    path_to_video: FilePath,
    frame_to_extract_time: str | int = "middle",
):
    cap = cv2.VideoCapture(str(path_to_video))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    msg = (
        f"frame_to_extract_time can only be defined as halfway, start, end, or integer; "
        f"not {type(frame_to_extract_time)}"
    )
    if isinstance(frame_to_extract_time, str):
        if (frame_to_extract_time := frame_to_extract_time.lower()) == "middle":
            target_frame_index = round(frame_count / 2.0)
        elif frame_to_extract_time == "start" or frame_to_extract_time == "beginning":
            target_frame_index = 0
        elif frame_to_extract_time == "end":
            target_frame_index = frame_count
        else:
            raise ValueError(msg)
    elif isinstance(frame_to_extract_time, int):
        target_frame_index = frame_to_extract_time
    else:
        raise TypeError(msg)

    cap.set(1, target_frame_index - 1)
    res, frame = cap.read()

    assert res, f"Could not extract frame from media, {path_to_video}"

    return frame


@validate_call
def extract_video(
    path_to_video: FilePath,
    include_image: bool = True,
    frame_to_extract_time: str | int = "middle",
) -> VideoMextractorMetadata:
    try:
        import ffmpeg
    except ImportError:
        msg = "Extra to extract video metadata not installed. Install by:\npip install mextractor[video-extract]"
        raise ImportError(msg)

    ffmpeg_probe = ffmpeg.probe(path_to_video)
    video_streams = [stream for stream in ffmpeg_probe["streams"] if stream["codec_type"] == "video"]

    if not video_streams:
        raise ValueError("No video stream found")

    # Assuming the first video stream is the one we want
    video_stream_metadata = video_streams[0]

    return VideoMextractorMetadata(
        name=path_to_video.stem,
        resolution=(video_stream_metadata["width"], video_stream_metadata["height"]),
        average_fps=video_stream_metadata["avg_frame_rate"],
        video_length_in_seconds=float(ffmpeg_probe["format"]["duration"]),
        image=extract_video_frame(path_to_video, frame_to_extract_time) if include_image else None,
    )
