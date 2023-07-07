from pathlib import Path
from dataclasses import dataclass
import datetime
from .session_dir import ISXDir

from typing import Union, Any, Optional, List


@dataclass
class IsxMouseDir:
    """
    A representation of a directory containing subdirectories for each session of a mouse.

    Subdirectories are expected to be ISXDirs, and will be parsed as such.

    Expected directory structure:
    ├── .
    │   ├── session_1
    │   │   ├── some_video.isxd
    │   │   ├── some_video_downsample.isxd
            ...
    │   ├── session_2
    │   │   ├── some_video.isxd
    │   │   ├── some_video_downsample.isxd
            ...
    │   ├── session_3
    │   │   ├── some_video.isxd
    │   │   ├── some_video_downsample.isxd
            ...

    """

    mouse_name: str
    mouse_dir: Path

    @classmethod
    def from_mouse_dir(cls, mouse_dir: Path):
        raise NotImplementedError


@dataclass
class AstrocyteSet1IsxMouseDir(IsxMouseDir):
    mouse_name: str
    mouse_dir: Path

    hab_cage_dir: ISXDir
    hab_cs_dir: ISXDir
    cond_dir: ISXDir
    ret_injection_dir: ISXDir
    ret_behavior_dir: ISXDir
    ext_injection_dir: ISXDir
    ext_behavior_dir: ISXDir
    ext_ret_dir: ISXDir
    long_ret_dir: ISXDir
    renew_dir: ISXDir

    @classmethod
    def from_mouse_dir(cls, mouse_dir: Path):
        # filter sub_dirs to only include those that end in six digits
        sub_dirs = [
            ISXDir.from_session_dir(d)
            for d in mouse_dir.glob("*")
            if d.is_dir() and d.name[-6:].isdigit()
        ]

        if len(sub_dirs) != 10:
            raise ValueError("Incorrect number of directories in mouse directory.")

        # order by date, they are in MMDDYY format
        sub_dirs = sorted(
            sub_dirs,
            key=lambda d: datetime.datetime.strptime(d.session_dir.name[-6:], "%m%d%y"),
        )

        hab_cage_dir = sub_dirs[0]
        hab_cs_dir = sub_dirs[1]
        cond_dir = sub_dirs[2]
        ret_behavior_dir, ret_injection_dir = sorted(
            (sub_dirs[3], sub_dirs[4]),
            key=lambda x: len(x.session_dir.name),
            reverse=True,
        )
        ext_behavior_dir, ext_injection_dir = sorted(
            (sub_dirs[5], sub_dirs[6]),
            key=lambda x: len(x.session_dir.name),
            reverse=True,
        )
        ext_ret_dir = sub_dirs[7]
        long_ret_dir = sub_dirs[8]
        renew_dir = sub_dirs[9]

        return cls(
            mouse_name=mouse_dir.name,
            mouse_dir=mouse_dir,
            hab_cage_dir=hab_cage_dir,
            hab_cs_dir=hab_cs_dir,
            cond_dir=cond_dir,
            ret_behavior_dir=ret_behavior_dir,
            ret_injection_dir=ret_injection_dir,
            ext_injection_dir=ext_injection_dir,
            ext_behavior_dir=ext_behavior_dir,
            ext_ret_dir=ext_ret_dir,
            long_ret_dir=long_ret_dir,
            renew_dir=renew_dir,
        )


@dataclass
class AstrocyteSet2IsxMouseDir(IsxMouseDir):
    mouse_name: str
    mouse_dir: Path

    hab_dir: ISXDir
    cond_dir: ISXDir
    ret_injection_dir: ISXDir
    ret_behavior_dir: ISXDir
    ext_injection_dir: ISXDir
    ext_behavior_dir: ISXDir
    ext_ret_dir: ISXDir
    long_ret_dir: ISXDir
    renew_dir: ISXDir

    @classmethod
    def from_mouse_dir(cls, mouse_dir: Path):
        # filter sub_dirs to only include those that end in six digits
        sub_dirs = [
            ISXDir.from_session_dir(d)
            for d in mouse_dir.glob("*")
            if d.is_dir() and d.name[-6:].isdigit()
        ]

        if len(sub_dirs) != 9:
            print(len(sub_dirs))
            sub_dirs = sorted(
                sub_dirs,
                key=lambda d: datetime.datetime.strptime(
                    d.session_dir.name[-6:], "%m%d%y"
                ),
            )
            print([sub_dirs.session_dir.name for sub_dirs in sub_dirs])
            raise ValueError("Incorrect number of directories in mouse directory.")

        # order by date, they are in MMDDYY format
        sub_dirs = sorted(
            sub_dirs,
            key=lambda d: datetime.datetime.strptime(d.session_dir.name[-6:], "%m%d%y"),
        )

        hab_dir = sub_dirs[0]
        cond_dir = sub_dirs[1]
        ret_behavior_dir, ret_injection_dir = sorted(
            (sub_dirs[2], sub_dirs[3]),
            key=lambda x: len(x.session_dir.name),
            reverse=True,
        )
        ext_behavior_dir, ext_injection_dir = sorted(
            (sub_dirs[4], sub_dirs[5]),
            key=lambda x: len(x.session_dir.name),
            reverse=True,
        )
        ext_ret_dir = sub_dirs[6]
        long_ret_dir = sub_dirs[7]
        renew_dir = sub_dirs[8]

        return cls(
            mouse_name=mouse_dir.name,
            mouse_dir=mouse_dir,
            hab_dir=hab_dir,
            cond_dir=cond_dir,
            ret_behavior_dir=ret_behavior_dir,
            ret_injection_dir=ret_injection_dir,
            ext_injection_dir=ext_injection_dir,
            ext_behavior_dir=ext_behavior_dir,
            ext_ret_dir=ext_ret_dir,
            long_ret_dir=long_ret_dir,
            renew_dir=renew_dir,
        )
