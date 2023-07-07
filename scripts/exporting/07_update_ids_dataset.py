from onep_preprocessing.path_parcers.output_dirs.output_root_parsers import (
    OutputRootParserAstrocyte,
)

from onep_preprocessing.exporting.update_ids import IDUpdaterDataset
from pathlib import Path
from tqdm import tqdm

GOOD_MICE_NUMS = (5, 8, 9, 13, 15, 22, 27, 30, 31, 6, 7, 12, 18, 24, 25, 28, 32)
DEST_DIR = Path(r"F:\astrocyte\export1")
ON_EXISTS = "overwrite"
MASTER_CELLSET_FILE = DEST_DIR / "master_cellset.csv"


def main():
    mouse_dirs = OutputRootParserAstrocyte.from_root_dir(
        DEST_DIR, numbers=GOOD_MICE_NUMS
    ).mouse_dirs

    id_updater = IDUpdaterDataset(
        dataset_cell_id="cell_id",
        mouse_cell_id="mouse_cell_id",
        on_exists=ON_EXISTS,
    )
    props_files = [mouse_dir.long_reg_tidy_csv for mouse_dir in mouse_dirs]

    master_cellset = id_updater.create_master_cellset(
        props_files=props_files,
        master_cellset_file=MASTER_CELLSET_FILE,
    )

    for mouse_dir in tqdm(mouse_dirs):
        mouse_name = mouse_dir.mouse_name
        for session_dir in (mouse_dir.ret_behavior_dir, mouse_dir.ext_behavior_dir):
            id_updater.update_traces(
                master_cellset=master_cellset,
                mouse_name=mouse_name,
                trace_file=session_dir.traces_tidy_mouse_id,
                updated_trace_file=session_dir.traces_tidy_mouse_dataset_id,
            )
            id_updater.update_props(
                master_cellset=master_cellset,
                mouse_name=mouse_name,
                props_file=session_dir.props_tidy_mouse_id,
                updated_props_file=session_dir.props_tidy_mouse_dataset_id,
            )


if __name__ == "__main__":
    main()
