from pathlib import Path
from .output_mouse_dir import OutputMouseDir, OutputMouseDirAstrocyte
from typing import List, Optional, Iterable, Sequence
from dataclasses import dataclass


@dataclass
class OutputRootParser:
    """
    A representation of the root directory containing data from a multiple mice.

    Subdirectories are expected to be OutputMouseDir, and will be parsed as such.

    Expected directory structure:

    ├── root_dir
    │   ├── mouse_1
    |   │   ├── session_1
    |   │   ├── session_2
    │   ├── mouse_2
    |   │   ├── session_1
    |   │   ├── session_2
    |   |  ...
    """

    root_dir: Path
    mouse_dirs: Sequence[OutputMouseDir]

    @classmethod
    def from_root_dir(cls, root_dir: Path):
        # filter sub_dirs to only include those that end in six digits
        sub_dirs = [
            sub_dir
            for sub_dir in root_dir.iterdir()
            if sub_dir.is_dir() and sub_dir.name.isdigit()
        ]
        mouse_dirs = [OutputMouseDir.from_mouse_dir(sub_dir) for sub_dir in sub_dirs]
        return cls(root_dir=root_dir, mouse_dirs=mouse_dirs)


@dataclass
class OutputRootParserAstrocyte(OutputRootParser):
    mouse_dirs: Sequence[OutputMouseDirAstrocyte]

    @classmethod
    def from_root_dir(cls, root_dir: Path, numbers: Optional[Iterable[int]] = None):
        mouse_dirs: List[OutputMouseDirAstrocyte] = []
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
                mouse_dirs.append(OutputMouseDirAstrocyte.from_mouse_dir(d))
            except ValueError:
                raise
        return cls(root_dir=root_dir, mouse_dirs=mouse_dirs)
