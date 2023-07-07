from onep_preprocessing.path_parcers.output_dirs.output_root_parsers import (
    OutputRootParserAstrocyte,
)
from onep_preprocessing.path_parcers.output_dirs.output_mouse_dir import (
    OutputMouseDirAstrocyte,
)

from onep_preprocessing.exporting.tidy_output import TraceTidier, PropsTidier
from typing import List, Iterable, Optional, Sequence
from pathlib import Path
from tqdm import tqdm

GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
DEST_DIR = Path(r"F:\astrocyte\export1")
ON_EXISTS = "skip"


def main():
    mouse_dirs = OutputRootParserAstrocyte.from_root_dir(
        DEST_DIR, numbers=GOOD_MICE_NUMS
    ).mouse_dirs

    trace_tidyer = TraceTidier(on_exists=ON_EXISTS)
    props_tidyer = PropsTidier(on_exists=ON_EXISTS)

    for mouse_dir in tqdm(mouse_dirs):
        for session_dir in (mouse_dir.ret_behavior_dir, mouse_dir.ext_behavior_dir):
            trace_tidyer(
                source_trace_file=session_dir.traces,
                output_trace_file=session_dir.traces_tidy,
            )
            props_tidyer(
                source_props_file=session_dir.props,
                output_props_file=session_dir.props_tidy,
            )


if __name__ == "__main__":
    main()
