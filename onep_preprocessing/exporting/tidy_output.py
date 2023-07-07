import isx
from typing import Optional, Sequence
from pathlib import Path
import pandas as pd


class Tidier:
    def __init__(self, on_exists: str = "overwrite"):
        self.on_exists = on_exists

    def if_exists(self, file: Path):
        if file.exists():
            if self.on_exists == "overwrite":
                file.unlink()
            elif self.on_exists == "raise":
                raise FileExistsError(f"{file} already exists")
            elif self.on_exists == "skip":
                return True


class TraceTidier(Tidier):
    def __init__(
        self,
        round_time: Optional[int] = 3,
        time_colname: str = "time",
        id_colname: str = "session_cell_id",
        value_colname: str = "value",
        on_exists: str = "overwrite",
    ):
        self.round_time = round_time
        self.time_colname = time_colname
        self.id_colname = id_colname
        self.value_colname = value_colname
        self.on_exists = on_exists

    def load_trace(self, trace_file: Path) -> pd.DataFrame:
        df = pd.read_csv(trace_file, skiprows=[1])
        df = df.rename(columns={" ": self.time_colname})
        return df

    def melt(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.melt(
            id_vars=self.time_colname,
            var_name=self.id_colname,
            value_name=self.value_colname,
        )
        return df

    def update_ids(self, df) -> pd.DataFrame:
        df[self.id_colname] = df[self.id_colname].apply(lambda x: int(x.split("C")[1]))
        return df

    def update_time(self, df) -> pd.DataFrame:
        df[self.time_colname] = df[self.time_colname].round(self.round_time)
        return df

    def tidy(self, trace_file: Path) -> pd.DataFrame:
        df = self.load_trace(trace_file)
        df = self.melt(df)
        df = self.update_ids(df)
        df = self.update_time(df)
        return df

    def __call__(self, source_trace_file: Path, output_trace_file: Path):
        df = self.tidy(source_trace_file)
        self.if_exists(output_trace_file)
        df.to_csv(output_trace_file, index=False)


class PropsTidier(Tidier):
    def __init__(
        self,
        id_colname: str = "session_cell_id",
        size_colname: str = "size",
        centroid_x_colname: str = "centroid_x",
        centroid_y_colname: str = "centroid_y",
        status_colname: str = "status",
        num_components_colname: str = "num_components",
        drop_active_segment: bool = True,
        drop_color: bool = True,
        existing_id_colname: str = "Name",
        existing_size_colname: str = "Size",
        existing_active_segment_colname: str = "ActiveSegment0",
        existing_centroid_x_colname: str = "CentroidX",
        existing_centroid_y_colname: str = "CentroidY",
        existing_color_colnames: Sequence[str] = ["ColorR", "ColorG", "ColorB"],
        existing_status_colname: str = "Status",
        existing_num_components_colname: str = "NumComponents",
        on_exists: str = "overwrite",
    ):
        self.id_colname = id_colname
        self.size_colname = size_colname
        self.drop_active_segment = drop_active_segment
        self.drop_color = drop_color
        self.centroid_x_colname = centroid_x_colname
        self.centroid_y_colname = centroid_y_colname
        self.status_colname = status_colname
        self.num_components_colname = num_components_colname

        self.existing_id_colname = existing_id_colname
        self.existing_size_colname = existing_size_colname
        self.existing_active_segment_colname = existing_active_segment_colname
        self.existing_centroid_x_colname = existing_centroid_x_colname
        self.existing_centroid_y_colname = existing_centroid_y_colname
        self.existing_color_colnames = existing_color_colnames
        self.existing_status_colname = existing_status_colname
        self.existing_num_components_colname = existing_num_components_colname

        self.on_exists = on_exists

    def load_props(self, props_file: Path) -> pd.DataFrame:
        df = pd.read_csv(props_file)
        return df

    def rename_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(
            columns={
                self.existing_id_colname: self.id_colname,
                self.existing_size_colname: self.size_colname,
                self.existing_centroid_x_colname: self.centroid_x_colname,
                self.existing_centroid_y_colname: self.centroid_y_colname,
                self.existing_status_colname: self.status_colname,
                self.existing_num_components_colname: self.num_components_colname,
            }
        )
        return df

    def update_ids(self, df) -> pd.DataFrame:
        df[self.id_colname] = df[self.id_colname].apply(lambda x: int(x.split("C")[1]))
        return df

    def drop_cols(self, df) -> pd.DataFrame:
        if self.drop_active_segment:
            df = df.drop(columns=[self.existing_active_segment_colname])
        if self.drop_color:
            df = df.drop(columns=[c for c in self.existing_color_colnames])
        return df

    def tidy(self, props_file: Path) -> pd.DataFrame:
        df = self.load_props(props_file)
        df = self.rename_cols(df)
        df = self.update_ids(df)
        df = self.drop_cols(df)
        return df

    def __call__(self, source_props_file: Path, output_props_file: Path):
        df = self.tidy(source_props_file)
        self.if_exists(output_props_file)
        df.to_csv(output_props_file, index=False)


class LongRegTidier(Tidier):
    def __init__(
        self,
        sessions: Sequence[str],
        mouse_cell_id: str = "mouse_cell_id",
        session_cell_id: str = "session_cell_id",
        session_colname: str = "session",
        session_index_col: str = "session_index",
        existing_mouse_cell_id: str = "global_cell_index",
        existing_session_cell_id: str = "local_cell_index",
        existing_session_colname: str = "local_cellset_index",
        on_exists: str = "overwrite",
    ) -> None:
        self.sessions = sessions
        self.mouse_cell_id = mouse_cell_id
        self.session_cell_id = session_cell_id
        self.session_colname = session_colname
        self.session_index_col = session_index_col
        self.existing_mouse_cell_id = existing_mouse_cell_id
        self.existing_session_cell_id = existing_session_cell_id
        self.existing_session_colname = existing_session_colname
        self.on_exists = on_exists

    def load_long_reg(self, long_reg_file: Path) -> pd.DataFrame:
        df = pd.read_csv(long_reg_file)
        return df

    def rename_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(
            columns={
                self.existing_mouse_cell_id: self.mouse_cell_id,
                self.existing_session_cell_id: self.session_cell_id,
                self.existing_session_colname: self.session_index_col,
            }
        )
        return df

    def map_sessions(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.session_colname] = df[self.session_index_col].apply(
            lambda x: self.sessions[x]
        )
        return df

    def tidy(self, long_reg_file: Path) -> pd.DataFrame:
        df = self.load_long_reg(long_reg_file)
        df = self.rename_cols(df)
        df = self.map_sessions(df)
        return df

    def __call__(self, source_long_reg_file: Path, output_long_reg_file: Path):
        df = self.tidy(source_long_reg_file)
        self.if_exists(output_long_reg_file)
        df.to_csv(output_long_reg_file, index=False)
