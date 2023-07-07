from pathlib import Path
from .output_session_dir import OutputDir
from typing import List, Optional, Iterable, Type, Sequence
from dataclasses import dataclass
import datetime


@dataclass
class OutputMouseDir:
    """
    A representation of the root directory of a hard drive containing data from a single mouse.

    Subdirectories are expected to be MouseDirs, and will be parsed as such.

    Expected directory structure:

    ├── mouse_1
    |   ├── long_reg.csv
    |   ├── long_reg_tidy.csv
    |   ├── long_reg_tidy_dataset_id.csv
    |   ├── long_reg_crop.csv
    |   ├── long_reg_translation.csv
    │   ├── session_1
    |   │   ├── traces.csv
    |   │   ├── traces_tidy.csv
    |   │   ├── traces_tidy_mouse_id.csv
    |   │   ├── traces_tidy_mouse_dataset_id.csv
    |   │   ├── props.csv
    |   │   ├── props_tidy.csv
    |   │   ├── props_tidy_mouse_id.csv
    |   │   ├── props_tidy_mouse_dataset_id.csv
    |   │   └── tiff
    |   │       ├── cell_0001.tif
    |   │       ├── cell_0002.tif
    |   │       ├── cell_0003.tif
    |   │       ├── cell_0004.tif
    |   |       ...
    │   ├── session_2
    |   │   ├── traces.csv
    |   │   ├── traces_tidy.csv
    |   |  ...

    """

    mouse_name: str
    mouse_dir: Path

    long_reg_csv: Path
    long_reg_tidy_csv: Path
    long_reg_tidy_dataset_id_csv: Path
    long_reg_crop_csv: Path
    long_reg_translation_csv: Path

    @classmethod
    def from_mouse_dir(cls, mouse_dir: Path):
        raise NotImplementedError


@dataclass
class OutputMouseDirAstrocyte(OutputMouseDir):
    mouse_name: str
    mouse_dir: Path

    cond_dir: OutputDir
    ret_injection_dir: OutputDir
    ret_behavior_dir: OutputDir
    ext_injection_dir: OutputDir
    ext_behavior_dir: OutputDir
    ext_ret_dir: OutputDir
    long_ret_dir: OutputDir
    renew_dir: OutputDir

    @staticmethod
    def is_hab_dir(session_dir: Path):
        return "hab" in session_dir.name

    @classmethod
    def from_mouse_dir(cls, mouse_dir: Path):
        # filter sub_dirs to only include those that end in six digits
        sub_dirs = [
            OutputDir.from_session_dir(d)
            for d in mouse_dir.glob("*")
            if d.is_dir() and d.name[-6:].isdigit() and not cls.is_hab_dir(d)
        ]

        # order by date, they are in MMDDYY format
        sub_dirs = sorted(
            sub_dirs,
            key=lambda d: datetime.datetime.strptime(d.session_dir.name[-6:], "%m%d%y"),
        )

        cond_dir = sub_dirs[0]
        ret_behavior_dir, ret_injection_dir = sorted(
            (sub_dirs[1], sub_dirs[2]),
            key=lambda x: len(x.session_dir.name),
            reverse=True,
        )
        ext_behavior_dir, ext_injection_dir = sorted(
            (sub_dirs[3], sub_dirs[4]),
            key=lambda x: len(x.session_dir.name),
            reverse=True,
        )
        ext_ret_dir = sub_dirs[5]
        long_ret_dir = sub_dirs[6]
        renew_dir = sub_dirs[7]

        long_reg_csv = mouse_dir / "long_reg.csv"
        long_reg_tidy_csv = mouse_dir / "long_reg_tidy.csv"
        long_reg_tidy_dataset_id_csv = mouse_dir / "long_reg_tidy_dataset_id.csv"
        long_reg_crop_csv = mouse_dir / "long_reg_crop.csv"
        long_reg_translation_csv = mouse_dir / "long_reg_translation.csv"


        return cls(
            mouse_name=mouse_dir.name,
            mouse_dir=mouse_dir,
            long_reg_csv=long_reg_csv,
            long_reg_tidy_csv=long_reg_tidy_csv,
            long_reg_tidy_dataset_id_csv=long_reg_tidy_dataset_id_csv,
            long_reg_crop_csv=long_reg_crop_csv,
            long_reg_translation_csv=long_reg_translation_csv,
            cond_dir=cond_dir,
            ret_behavior_dir=ret_behavior_dir,
            ret_injection_dir=ret_injection_dir,
            ext_injection_dir=ext_injection_dir,
            ext_behavior_dir=ext_behavior_dir,
            ext_ret_dir=ext_ret_dir,
            long_ret_dir=long_ret_dir,
            renew_dir=renew_dir,
        )
