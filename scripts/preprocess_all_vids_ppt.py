from pathlib import Path
from typing import List
from onep_preprocessing.preprocess import preprocess

ROOT_DIR = Path(r"")  # change this path to where your videos are stored


def find_video_paths(root_directory: Path) -> List[Path]:
    """Find all inscopix .isxd raw video files below a root directory

    Args:
        root_directory (Path): Path to root directory

    Returns:
        List[Path]: List of pathlib.Path objects containing paths to raw video files
    """
    # write a function here that will find the paths to your videos
    pass


def generate_output_dir(input_video_path: Path) -> Path:
    """Given a video to be preprocessed, returns a directory where all of the preprocessed files will be saved

    Args:
        input_video_path (Path): Path to raw .isxd file

    Returns:
        Path: Path to directory where all preprocessed files will be saved
    """
    # change this to alter the location of the preprocessed files
    outdir = input_video_path.parent / "preprocessed"
    outdir.mkdir(exist_ok=True, parents=True)
    return outdir


def main() -> None:
    vids = find_video_paths(ROOT_DIR)
    for vid in vids:
        output_dir = generate_output_dir(vid)
        preprocess(in_path=vid, out_dir=output_dir)
