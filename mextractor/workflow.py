import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from shutil import rmtree
from typing import Iterable

from pydantic import DirectoryPath, FilePath, validate_call

from mextractor.base import ImageMextractorMetadata, VideoMextractorMetadata
from mextractor.extractors import extract_image, extract_video, extract_video_frame
from mextractor.utils import dump_image


def extract_and_dump_image(
    dump_dir: DirectoryPath,
    path_to_image: FilePath,
    include_image: bool = True,
    lossy_compress_image: bool = True,
) -> ImageMextractorMetadata:
    metadata = extract_image(path_to_image, include_image)
    metadata.dump(dump_dir, include_image, lossy_compress_image)
    return metadata


def extract_and_dump_video(
    dump_dir: DirectoryPath,
    path_to_video: FilePath,
    include_image: bool = True,
    lossy_compress_image: bool = True,
) -> VideoMextractorMetadata:
    metadata = extract_video(path_to_video, include_image)
    metadata.dump(dump_dir, include_image, lossy_compress_image)
    return metadata


@validate_call
def mextract_videos_in_subdirs(
    root_dir: DirectoryPath, video_file_suffixes: Iterable[str], only_frame: bool = False
) -> None:
    """
    Copy directory to a new directory while extracting media info and a single frame from videos in subdirectories
    """
    new_root = root_dir.with_name(f"{root_dir.name}_mextracted")
    if new_root.exists():
        rmtree(new_root)
    new_root.mkdir()

    futures = []
    with ThreadPoolExecutor() as executor:
        for source_path in root_dir.glob("**/*.*"):
            dest_path = new_root / source_path.relative_to(root_dir)
            dest_dir = dest_path.parent

            os.makedirs(dest_dir, exist_ok=True)

            for video_file_suffix in video_file_suffixes:
                if video_file_suffix and dest_path.suffix in video_file_suffix:
                    if only_frame:
                        futures.append(
                            executor.submit(
                                dump_image,
                                extract_video_frame(source_path),
                                dest_dir,
                                source_path.stem,
                                lossy_compress_image=False,
                            )
                        )
                    else:
                        futures.append(
                            executor.submit(extract_and_dump_video, dest_dir, source_path, include_image=True)
                        )
            else:
                futures.append(executor.submit(shutil.copy, source_path, dest_path))

    for future in futures:
        try:
            future.result()
        except Exception as e:
            shutil.rmtree(dest_dir)
            raise e
