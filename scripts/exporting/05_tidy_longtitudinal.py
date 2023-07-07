from onep_preprocessing.path_parcers.output_dirs.output_root_parsers import (
    OutputRootParserAstrocyte,
)
from onep_preprocessing.exporting.tidy_output import LongRegTidier
from pathlib import Path
from tqdm import tqdm

GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
DEST_DIR = Path(r"F:\astrocyte\export1")
ON_EXISTS = "overwrite"


def main():
    mouse_dirs = OutputRootParserAstrocyte.from_root_dir(
        DEST_DIR, numbers=GOOD_MICE_NUMS
    ).mouse_dirs

    tidier = LongRegTidier(
        sessions=("ret", "ext"),
        session_cell_id="session_cell_id",
        mouse_cell_id="mouse_cell_id",
        on_exists=ON_EXISTS,
    )

    for mouse_dir in tqdm(mouse_dirs):
        tidier(source_long_reg_file=mouse_dir.long_reg_csv, output_long_reg_file=mouse_dir.long_reg_tidy_csv)


if __name__ == "__main__":
    main()
