from pathlib import Path
from dataclasses import dataclass
import datetime
from typing import Union, Any, Optional, List


@dataclass
class OutputDir:
    """
    Representation of a directory that contains exported inscopix files from a recording session.

    Will return paths even if they are not currently present on the hard drive.

    Expected directory structure:

    ├── .
    │   ├── traces.csv
    │   ├── traces_tidy.csv
    │   ├── traces_tidy_mouse_id.csv
    │   ├── traces_tidy_mouse_dataset_id.csv
    │   ├── props.csv
    │   ├── props_tidy.csv
    │   ├── props_tidy_mouse_id.csv
    │   ├── props_tidy_mouse_dataset_id.csv
    │   └── tiff
    │       ├── cell_0001.tif


    """                                                                    

    session_dir: Path
    traces: Optional[Path]
    traces_tidy: Optional[Path]
    traces_tidy_mouse_id: Optional[Path]
    traces_tidy_mouse_dataset_id: Optional[Path]
    props: Optional[Path]
    props_tidy: Optional[Path]
    props_tidy_mouse_id: Optional[Path]
    props_tidy_mouse_dataset_id: Optional[Path]
    tiff: Optional[Path]

    @classmethod
    def from_session_dir(cls, session_dir: Path):
        # return expected paths even if they do not currently exist
        session_dir = session_dir

        traces = session_dir / "traces.csv"
        traces_tidy = session_dir / "traces_tidy.csv"
        traces_tidy_mouse_id = session_dir / "traces_tidy_mouse_id.csv"
        traces_tidy_mouse_dataset_id = session_dir / "traces_tidy_mouse_dataset_id.csv"
        props = session_dir / "props.csv"
        props_tidy = session_dir / "props_tidy.csv"
        props_tidy_mouse_id = session_dir / "props_tidy_mouse_id.csv"
        props_tidy_mouse_dataset_id = session_dir / "props_tidy_mouse_dataset_id.csv"
        tiff = session_dir / "tiff"


        return cls(
            session_dir=session_dir,
            traces=traces,
            traces_tidy=traces_tidy,
            traces_tidy_mouse_id=traces_tidy_mouse_id,
            traces_tidy_mouse_dataset_id=traces_tidy_mouse_dataset_id,
            props=props,
            props_tidy=props_tidy,
            props_tidy_mouse_id=props_tidy_mouse_id,
            props_tidy_mouse_dataset_id=props_tidy_mouse_dataset_id,
            tiff=tiff,
        )
