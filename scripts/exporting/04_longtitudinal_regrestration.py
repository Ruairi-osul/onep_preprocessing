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

from onep_preprocessing.exporting.longreg import IsxLongtitudinalRegistration
from typing import List, Iterable, Optional, Sequence
from pathlib import Path
from tqdm import tqdm


GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
SOURCE_DIR = Path(r"D:\raw data")
DEST_DIR = Path(r"F:\astrocyte\export1")
ON_EXISTS = "overwrite"


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

    long_reg = IsxLongtitudinalRegistration(
        min_correlation=0.4, accepted_cells_only=True, on_exists=ON_EXISTS
    )

    for source_mouse_dir in tqdm(source_mouse_dirs):
        target_mouse_dir = get_mouse_dir(source_mouse_dir, target_mouse_dirs)
        input_cellsets = [
            source_mouse_dir.ret_behavior_dir.cnmfe_cellset,
            source_mouse_dir.ext_behavior_dir.cnmfe_cellset,
        ]
        output_csv_file = target_mouse_dir.long_reg_csv
        long_reg(
            cellset_files=input_cellsets,
            output_csv_file=output_csv_file,
            transform_csv_file=target_mouse_dir.long_reg_translation_csv,
            crop_csv_file=target_mouse_dir.long_reg_crop_csv,
        )


if __name__ == "__main__":
    main()
