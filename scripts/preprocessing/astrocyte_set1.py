from onep_preprocessing.processors.dispatcher import PreprocessorDispatcher
from onep_preprocessing.processors.preprocessors import (
    ISXDownSampler,
    ISXSpatialFilterer,
    ISXMotionCorrector,
    ISXDff,
)
from onep_preprocessing.processors.cnmfe import ISXCNMFe
from onep_preprocessing.path_parcers.raw_data_dirs.isx_root_parsers import (
    IsxRootParserAstrocyteSet1,
)
from pathlib import Path
from tqdm import tqdm

GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
ON_EXISTS = "skip"
CNMFE_NUM_THREADS = 10
ROOT_DIR = Path(r"D:")


def main():
    root_parcer = IsxRootParserAstrocyteSet1.from_root_dir(ROOT_DIR, numbers=GOOD_MICE_NUMS)
    mouse_dirs = root_parcer.mouse_dirs
    dispatcher = PreprocessorDispatcher(
        downsampler=ISXDownSampler(),
        spatial_filterer=ISXSpatialFilterer(),
        motion_corrector=ISXMotionCorrector(),
        dff=ISXDff(),
        on_exists="overwrite",
    )
    for mouse_dir in tqdm(mouse_dirs, desc="Mice"):
        for session_dir in tqdm(
            [mouse_dir.ret_behavior_dir, mouse_dir.ext_behavior_dir],
            desc=f"{mouse_dir.mouse_name} sessions",
        ):
            dispatcher(isx_video=session_dir.raw_movie)


if __name__ == "__main__":
    main()
