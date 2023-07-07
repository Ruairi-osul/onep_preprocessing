from onep_preprocessing.path_parcers.raw_data_dirs.isx_root_parsers import (
    IsxRootParserAstrocyteSet1,
)
from onep_preprocessing.exporting.dir_copy import DirectoryCopier
from typing import List, Iterable, Optional
from pathlib import Path
from tqdm import tqdm

GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
SOURCE_DIR = Path(r"D:\raw data")
DEST_DIR = Path(r"F:\astrocyte\export1")


def main():
    copier = DirectoryCopier(depth=2)
    copier.copy_directories(source=SOURCE_DIR, target=DEST_DIR)


if __name__ == "__main__":
    main()
