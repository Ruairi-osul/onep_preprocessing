from pathlib import Path
from .isx_mouse_dir import IsxMouseDir, AstrocyteSet1IsxMouseDir, AstrocyteSet2IsxMouseDir
from typing import List, Optional, Iterable, Sequence
from dataclasses import dataclass


@dataclass
class IsxRootParser:
    """
    A representation of the root directory of a hard drive containing data from a single mouse.

    Subdirectories are expected to be MouseDirs, and will be parsed as such.

    Expected directory structure:
    ├── .
    │   ├── mouse_1
    │   │   ├── session_1
    │   │   │   ├── some_video.isxd
    │   │   │   ├── some_video_downsample.isxd
    │   │   │   ├── some_video_spatial.isxd
    │   │   │   ├── some_video_motion.isxd
    │   │   │   ├── some_video_cnmfe.isxd
    │   │   │   ├── some_video_dff.isxd
    │   │   │   ├── some_video.gpio
    │   │   │   └── some_video.imu
    │   │   ├── session_2
    │   │   │   ├── some_video.isxd
    │   │   │   ├── some_video_downsample.isxd
    │   │   │   ├── some_video_spatial.isxd
    │   │   │   ├── some_video_motion.isxd
    │   │   │   ├── some_video_cnmfe.isxd
    │   │   │   ├── some_video_dff.isxd
    │   │   │   ├── some_video.gpio
    │   │   │   └── some_video.imu
    │   │   ├── session_3
    │   │   │   ├── some_video.isxd
    │   │   │   ├── some_video_downsample.isxd
    │   │   │   ├── some_video_spatial.isxd
    │   │   │   ├── some_video_motion.isxd
    │   │   │   ├── some_video_cnmfe.isxd
    │   │   │   ├── some_video_dff.isxd
    │   │   │   ├── some_video.gpio
    │   │   │   └── some_video.imu
    │   ├── mouse_2
    │   │   ├── session_1
    │   │   │   ├── some_video.isxd
    │   │   │   ├── some_video_downsample.isxd
    │   │   │   ├── some_video_spatial.isxd
    │   │   │   ...
    """

    root_dir: Path
    mouse_dirs: Sequence[IsxMouseDir]

    @classmethod
    def from_root_dir(cls, root_dir: Path):
        # filter sub_dirs to only include those that end in six digits
        sub_dirs = [
            sub_dir
            for sub_dir in root_dir.iterdir()
            if sub_dir.is_dir() and sub_dir.name.isdigit()
        ]
        mouse_dirs = [IsxMouseDir.from_mouse_dir(sub_dir) for sub_dir in sub_dirs]
        return cls(root_dir=root_dir, mouse_dirs=mouse_dirs)


@dataclass
class IsxRootParserAstrocyteSet1(IsxRootParser):
    mouse_dirs: Sequence[AstrocyteSet1IsxMouseDir]

    @classmethod
    def from_root_dir(cls, root_dir: Path, numbers: Optional[Iterable[int]] = None):
        mouse_dirs: List[AstrocyteSet1IsxMouseDir] = []
        for d in root_dir.glob("*"):
            if not d.is_dir():
                continue
            if not d.name.startswith("A"):
                continue
            if numbers:
                subdir_number = int(d.name.split("-")[-1])
                if subdir_number not in numbers:
                    continue
            try:
                mouse_dirs.append(AstrocyteSet1IsxMouseDir.from_mouse_dir(d))
            except ValueError:
                print(d.name)
                raise
        return cls(root_dir=root_dir, mouse_dirs=mouse_dirs)


@dataclass
class IsxRootParserAstrocyteSet2(IsxRootParser):
    mouse_dirs: Sequence[AstrocyteSet2IsxMouseDir]

    @classmethod
    def from_root_dir(cls, root_dir: Path, numbers: Optional[Iterable[int]] = None):
        mouse_dirs: List[AstrocyteSet2IsxMouseDir] = []
        for d in root_dir.glob("*"):
            if not d.is_dir():
                continue
            if not d.name.startswith("A"):
                continue
            if numbers:
                subdir_number = int(d.name.split("-")[-1])
                if subdir_number not in numbers:
                    continue
            try:
                mouse_dirs.append(AstrocyteSet2IsxMouseDir.from_mouse_dir(d))
            except ValueError:
                print(d.name)
                raise
        return cls(root_dir=root_dir, mouse_dirs=mouse_dirs)
