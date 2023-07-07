from pathlib import Path
from dataclasses import dataclass
import datetime
from typing import Union, Any, Optional, List


@dataclass
class ISXDir:
    """
    Representation of a directory that contains inscopix files from a recording session.

    Expected directory structure:  

    ├── .
    │   ├── some_video.isxd
    │   ├── some_video_downsample.isxd
    │   ├── some_video_spatial.isxd
    │   ├── some_video_motion.isxd
    │   ├── some_video_cnmfe.isxd
    │   ├── some_video_dff.isxd
    │   ├── some_video.gpio
    │   └── some_video.imu

    
    All optional and will be set to None if not found.
    """
    session_dir: Path
    raw_movie: Optional[Path]
    gpio: Optional[Path]
    imu: Optional[Path]

    downsampled: Optional[Path]
    spatial_filtered: Optional[Path]
    motion_corrected: Optional[Path]
    cnmfe_cellset: Optional[Path]
    dff: Optional[Path]

    @classmethod
    def from_session_dir(cls, session_dir: Path):
        session_dir = session_dir
        # get list of all isxd files
        isxd_files = list(session_dir.glob("*.isxd"))
        # if one contains 'downsample', assign to downsampled
        downsampled = next((f for f in isxd_files if "downsample" in f.name), None)
        # if one contains 'spatial', assign to spatial_filtered
        spatial_filtered = next((f for f in isxd_files if "spatial" in f.name), None)
        # if one contains 'motion', assign to motion_corrected
        motion_corrected = next((f for f in isxd_files if "motion" in f.name), None)
        # if one contains 'cnmfe', assign to cnmfe_cellset
        cnmfe_cellset = next((f for f in isxd_files if "cnmfe" in f.name), None)
        # if one contains 'dff', assign to dff
        dff = next((f for f in isxd_files if "dff" in f.name), None)
        # if there are any left, assign to raw_movie
        raw_movie = next(
            (
                f
                for f in isxd_files
                if f
                not in [
                    downsampled,
                    spatial_filtered,
                    motion_corrected,
                    cnmfe_cellset,
                    dff,
                ]
            ),
            None,
        )

        # get the gpio and imu files and assign to gpio and imu, set to None if not found
        gpio = next((f for f in session_dir.glob("*.gpio")), None)

        imu = next((f for f in session_dir.glob("*.imu")), None)

        return cls(
            session_dir=session_dir,
            raw_movie=raw_movie,
            gpio=gpio,
            imu=imu,
            downsampled=downsampled,
            spatial_filtered=spatial_filtered,
            motion_corrected=motion_corrected,
            cnmfe_cellset=cnmfe_cellset,
            dff=dff,
        )
