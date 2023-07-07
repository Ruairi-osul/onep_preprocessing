from onep_preprocessing.path_parcers.raw_data_dirs.isx_root_parsers import (
    IsxRootParserAstrocyteSet1,
)
from onep_preprocessing.path_parcers.raw_data_dirs.isx_mouse_dir import (
    AstrocyteSet1IsxMouseDir,
)
from onep_preprocessing.path_parcers.output_dirs.output_root_parsers import (
    OutputRootParserAstrocyte,
)
from onep_preprocessing.path_parcers.output_dirs.output_mouse_dir import (
    OutputMouseDirAstrocyte,
)

from onep_preprocessing.exporting.export_isx_files import IsxExporter
from typing import List, Iterable, Optional, Sequence
from pathlib import Path
from tqdm import tqdm

GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
SOURCE_DIR = Path(r"D:\raw data")
DEST_DIR = Path(r"F:\astrocyte\export1")
ON_EXISTS = "skip"

TRACE_FILENAME = "traces.csv"
PROPS_FILENAME = "props.csv"
TIFF_SUBDIR = "tiff"
TIFF_FILENAME = "tiff.tif"


def get_mouse_dir(
    source: AstrocyteSet1IsxMouseDir, target_dirs: Sequence[OutputMouseDirAstrocyte]
) -> Optional[OutputMouseDirAstrocyte]:

    for target in target_dirs:
        if source.mouse_name == target.mouse_name:
            return target
    return None


def main():
    source_mouse_dirs = IsxRootParserAstrocyteSet1.from_root_dir(
        SOURCE_DIR, numbers=GOOD_MICE_NUMS
    ).mouse_dirs
    target_mouse_dirs = OutputRootParserAstrocyte.from_root_dir(
        DEST_DIR, numbers=GOOD_MICE_NUMS
    ).mouse_dirs

    isx_exporter = IsxExporter(
        trace_filename=TRACE_FILENAME,
        props_filename=PROPS_FILENAME,
        tiff_subdir=TIFF_SUBDIR,
        tiff_filename=TIFF_FILENAME,
        on_exists=ON_EXISTS,
    )

    for source_mouse_dir in tqdm(source_mouse_dirs):
        target_mouse_dir = get_mouse_dir(source_mouse_dir, target_mouse_dirs)

        for source_session_dir, target_session_dir in zip(
            [source_mouse_dir.ret_behavior_dir, source_mouse_dir.ext_behavior_dir],
            [target_mouse_dir.ret_behavior_dir, target_mouse_dir.ext_behavior_dir],
        ):

            isx_exporter(
                cellset_file=source_session_dir.cnmfe_cellset,
                output_dir=target_session_dir.session_dir,
            )


if __name__ == "__main__":
    main()
