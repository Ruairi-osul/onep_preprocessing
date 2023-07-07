from onep_preprocessing.path_parcers.output_dirs.output_root_parsers import (
    OutputRootParserAstrocyte,
)

from onep_preprocessing.exporting.update_ids import IDUpdaterMouse
from pathlib import Path
from tqdm import tqdm

GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
DEST_DIR = Path(r"F:\astrocyte\export1")
ON_EXISTS = "overwrite"


def main():
    mouse_dirs = OutputRootParserAstrocyte.from_root_dir(
        DEST_DIR, numbers=GOOD_MICE_NUMS
    ).mouse_dirs

    id_updater = IDUpdaterMouse(session_cell_id="session_cell_id", mouse_cell_id="mouse_cell_id", on_exists=ON_EXISTS)

    for mouse_dir in tqdm(mouse_dirs):
        for session_dir in (mouse_dir.ret_behavior_dir, mouse_dir.ext_behavior_dir):
            id_updater.update_traces(
                longreg_file=mouse_dir.long_reg_tidy_csv,
                trace_file=session_dir.traces_tidy,
                updated_trace_file=session_dir.traces_tidy_mouse_id
            )
            id_updater.update_props(
                longreg_file=mouse_dir.long_reg_tidy_csv,
                props_file=session_dir.props_tidy,
                updated_props_file=session_dir.props_tidy_mouse_id
            )


if __name__ == "__main__":
    main()
