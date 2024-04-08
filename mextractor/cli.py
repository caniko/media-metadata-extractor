
import typer
from pydantic import DirectoryPath
from typing_extensions import Annotated

from mextractor.constants import VIDEO_SUFFIXES
from mextractor.workflow import mextract_videos_in_subdirs

cli_app = typer.Typer()


@cli_app.command()
def extract(
    start_dir: Annotated[
        DirectoryPath,
        typer.Argument(
            help="The directory to start the scan; every subdir will be checked. Default to CWD or working directory.",
        ),
    ],
    video_suffixes: Annotated[
        list[str], typer.Option(help="Limit the suffixes that will be scanned, omit to include all")
    ] = VIDEO_SUFFIXES,
    only_frame: Annotated[bool, typer.Option(is_flag=True, flag_value=True)] = False,
) -> None:
    mextract_videos_in_subdirs(start_dir, video_suffixes, only_frame=only_frame)
