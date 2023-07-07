import pandas as pd
from pathlib import Path
from typing import Sequence, Optional


class IDUpdater:
    def __init__(
        self,
        on_exists: str = "overwrite",
    ):

        self.on_exists = on_exists

    def if_exists(self, file: Path):
        if file.exists():
            if self.on_exists == "overwrite":
                file.unlink()
            elif self.on_exists == "raise":
                raise FileExistsError(f"{file} already exists")
            elif self.on_exists == "skip":
                return True


class IDUpdaterMouse(IDUpdater):
    def __init__(
        self,
        session_cell_id: str = "session_cell_id",
        mouse_cell_id: str = "mouse_cell_id",
        on_exists: str = "overwrite",
    ):

        self.session_cell_id = session_cell_id
        self.mouse_cell_id = mouse_cell_id
        self.on_exists = on_exists

    def update_traces(
        self, longreg_file: Path, trace_file: Path, updated_trace_file: Path
    ) -> None:
        traces = pd.read_csv(trace_file)
        longreg = pd.read_csv(longreg_file)

        traces = traces.merge(
            longreg[[self.session_cell_id, self.mouse_cell_id]].drop_duplicates(),
            on=self.session_cell_id,
        )
        traces = traces.drop(columns=[self.session_cell_id])
        self.if_exists(updated_trace_file)
        traces.to_csv(updated_trace_file, index=False)

    def update_props(
        self, longreg_file: Path, props_file: Path, updated_props_file: Path
    ) -> None:
        props = pd.read_csv(props_file)
        longreg = pd.read_csv(longreg_file)

        props = props.merge(
            longreg[[self.session_cell_id, self.mouse_cell_id]].drop_duplicates(),
            on=self.session_cell_id,
        )
        props = props.drop(columns=[self.session_cell_id])
        self.if_exists(updated_props_file)
        props.to_csv(updated_props_file, index=False)


class IDUpdaterDataset(IDUpdater):
    def __init__(
        self,
        dataset_cell_id: str = "cell_id",
        mouse_cell_id: str = "mouse_cell_id",
        mouse_name_col: str = "mouse_name",
        on_exists: str = "overwrite",
    ):
        self.dataset_cell_id = dataset_cell_id
        self.mouse_cell_id = mouse_cell_id
        self.mouse_name_col = mouse_name_col
        self.on_exists = on_exists

    def create_master_cellset(
        self,
        props_files: Sequence[Path],
        master_cellset_file: Optional[Path] = None,
    ) -> pd.DataFrame:

        master_cellset = pd.DataFrame()
        for props_file in props_files:
            mouse_name = props_file.parent.name
            props = pd.read_csv(props_file)
            props[self.mouse_name_col] = mouse_name
            master_cellset = master_cellset.append(
                props[[self.mouse_cell_id, self.mouse_name_col]]
            )
        master_cellset = master_cellset.drop_duplicates().reset_index(drop=True)
        master_cellset[self.dataset_cell_id] = range(len(master_cellset))

        if master_cellset_file is not None:
            self.if_exists(master_cellset_file)
            master_cellset.to_csv(master_cellset_file, index=False)
        return master_cellset

    def update_traces(
        self,
        master_cellset: pd.DataFrame,
        mouse_name: str,
        trace_file: Path,
        updated_trace_file: Path,
    ) -> None:
        self.if_exists(updated_trace_file)
        traces = pd.read_csv(trace_file)
        traces = traces.merge(
            master_cellset[master_cellset[self.mouse_name_col] == mouse_name],
            on=self.mouse_cell_id,
        )
        traces = traces.drop(columns=[self.mouse_cell_id])
        traces.to_csv(updated_trace_file, index=False)

    def update_props(
        self,
        master_cellset: pd.DataFrame,
        mouse_name: str,
        props_file: Path,
        updated_props_file: Path,
    ) -> None:
        self.if_exists(updated_props_file)
        props = pd.read_csv(props_file)
        props = props.merge(
            master_cellset[master_cellset[self.mouse_name_col] == mouse_name],
            on=self.mouse_cell_id,
        )
        props = props.drop(columns=[self.mouse_cell_id])
        props.to_csv(updated_props_file, index=False)
