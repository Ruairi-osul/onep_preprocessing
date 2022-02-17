from os import cpu_count
from typing import Callable, Iterable, List, Optional, Dict, Union, Optional
from dataclasses import dataclass
from pathlib import Path
from enum import Enum, auto
import shutil
from collections import OrderedDict
import pandas as pd
import numpy as np
import isx
import re
from pathmodels.base.data_dirs import OnePDir
from pathmodels.pfc.mouse_dir import PFCMouseDir
import tempfile


class Cohort(Enum):
    OFLNEW = auto()
    PFC = auto()


@dataclass()
class SessionData:
    cellset_file: Path
    gpio_file: Union[Path, None] = None


class FileFinder:
    def __init__(self, path: Path, cohort: Cohort) -> None:
        self.path = path
        self.find_method = self._find_files_fac(cohort)

    def _find_files_fac(self, cohort: Cohort) -> Callable[[], SessionData]:
        if cohort is Cohort.OFLNEW:
            return self._find_files_ofl_new
        elif cohort is Cohort.PFC:
            return self._find_files_pfc
        else:
            raise ValueError()

    def _find_files_ofl_new(self) -> SessionData:
        data = SessionData(cellset_file=self.path.joinpath("cnmfe_cellset.isxd"))
        return data

    def _find_files_pfc(self) -> SessionData:
        data_dir = OnePDir.from_path(self.path)
        data = SessionData(data_dir.cellset_file)
        return data

    def find(self) -> SessionData:
        """Find imaging files in a session

        Returns:
            SessionData: Object containing paths to imaging data in inscopix format to be exported
        """
        return self.find_method()


class SessionDirsFinder:
    def __init__(self, path: Path, cohort: Cohort) -> None:
        self.path = path
        self.find_method = self._find_dirs_fac(cohort)

    def _find_dirs_fac(self, cohort: Cohort) -> Callable[[], Dict[str, Path]]:
        if cohort is Cohort.OFLNEW:
            return self._find_dirs_oflnew
        elif cohort is Cohort.PFC:
            return self._find_dirs_pfc
        else:
            return ValueError()

    def _find_dirs_pfc(self) -> Dict[str, Path]:
        mouse_dir = PFCMouseDir.from_path(self.path)
        session_dirs: Dict[str, Path] = {}
        for session_name, session_dir in mouse_dir.session_dirs.items():
            if session_name == "day0-habituation":
                continue
            onep_dir = session_dir.data_dirs.get("one_photon")
            if onep_dir is not None:
                session_dirs[session_name] = onep_dir.path
        return session_dirs

    def _find_dirs_oflnew(
        self,
    ) -> Dict[str, Path]:
        d = OrderedDict()
        dirs = [d for d in self.path.glob("*") if d.is_dir()]
        d["day1"] = [d for d in dirs if re.search(r"[dD]ay1", str(d))][0]
        d["day2"] = [d for d in dirs if re.search(r"[dD]ay2", str(d))][0]
        d["day3"] = [d for d in dirs if re.search(r"[dD]ay3", str(d))][0]
        d["day4"] = [d for d in dirs if re.search(r"[dD]ay4", str(d))][0]
        return d

    def find(self) -> Dict[str, Path]:
        return self.find_method()


def longreg(
    cellsets: Iterable[str],
    *,
    output_dir: Path,
    delete_if_exists: bool = True,
    excluded_sessions_indexes: List[int] = None,
) -> Path:
    if excluded_sessions_indexes is None:
        excluded_sessions_indexes = []
    tmp_dir = Path(tempfile.gettempdir())
    output_cellsets = [
        str(tmp_dir / (str(i) + Path(f).name)) for i, f in enumerate(cellsets)
    ]
    logreg_file = str(output_dir / "logreg_file.csv")
    if delete_if_exists:
        for file in [logreg_file] + output_cellsets:
            f = Path(file)
            if f.exists():
                f.unlink()

    isx.longitudinal_registration(
        input_cell_set_files=cellsets,
        output_cell_set_files=output_cellsets,
        csv_file=logreg_file,
        accepted_cells_only=True,
        min_correlation=0.4,
    )
    df = pd.read_csv(logreg_file).rename(
        columns={
            "global_cell_index": "cell_id",
            "local_cell_index": "session_cell_id",
            "local_cellset_index": "session_index",
        }
    )
    for session_index in excluded_sessions_indexes:
        df.loc[df["session_index"] >= session_index] = (
            df.loc[df["session_index"] >= session_index].astype(int) + 1
        )

    df.to_csv(logreg_file, index=False)
    return Path(logreg_file)


@dataclass
class ExportPaths:
    traces: Path
    trace_props: Path
    spikes: Path
    spikes_props: Path
    gpio: Path
    tiff: Path


class ExportFileFinder:
    def __init__(
        self,
        session_name: str,
        output_root_dir: Path,
        mouse_path: Path,
        cohort: Cohort,
        unlink: bool = True,
    ) -> None:
        self.session_name = session_name
        self.output_doot_dir = output_root_dir
        self.mouse_path = mouse_path
        self.unlink = unlink
        self._method = self._method_fac(cohort)

    def _method_fac(self, cohort: Cohort) -> Callable[[], ExportPaths]:
        if cohort is Cohort.OFLNEW:
            return self._exports_oflnew
        elif cohort is Cohort.PFC:
            return self._exports_pfc
        else:
            raise ValueError()

    def _exports_oflnew(self) -> ExportPaths:
        output_dir = self.output_doot_dir / self.mouse_path.name / self.session_name
        export_paths = ExportPaths(
            traces=output_dir / "traces.csv",
            trace_props=output_dir / "trace_props.csv",
            tiff=output_dir / "tiff" / "cell_image.tiff",
            spikes=output_dir / "spikes.csv",
            spikes_props=output_dir / "spikes_props.csv",
            gpio=output_dir / "gpio.csv",
        )
        export_paths.tiff.parent.mkdir(exist_ok=True, parents=True)
        if self.unlink:
            self._unlink(export_paths)
        return export_paths

    def _exports_pfc(self) -> ExportPaths:
        return self._exports_oflnew()

    @staticmethod
    def _unlink(export_paths: ExportPaths) -> None:
        for p in (
            export_paths.traces,
            export_paths.trace_props,
            export_paths.spikes,
            export_paths.spikes_props,
            export_paths.gpio,
        ):
            if p.exists():
                p.unlink()
        shutil.rmtree(export_paths.tiff.parent)
        export_paths.tiff.parent.mkdir()

    def find(self) -> ExportPaths:
        return self._method()


class ISXFileExporter:
    def __init__(self, logreg_file: Path, session_index: int) -> None:
        self.logreg_file = logreg_file
        self.session_index = session_index

    @staticmethod
    def tidy_cell_ids(ser: pd.Series) -> pd.Series:
        return ser.apply(lambda x: int(x.split("C")[1]))

    def export_traces(
        self,
        src: Path,
        dest_traces: Path,
        dest_props: Path,
        dest_tiff: Path,
        update_cellids: bool = True,
    ) -> None:
        isx.export_cell_set_to_csv_tiff(
            input_cell_set_files=str(src),
            output_csv_file=str(dest_traces),
            output_tiff_file=str(dest_tiff),
            output_props_file=str(dest_props),
        )
        if update_cellids:
            master_cellset = pd.read_csv(self.logreg_file)
            master_cellset = master_cellset.loc[
                lambda x: x.session_index == self.session_index
            ]
            master_cellset = master_cellset[["cell_id", "session_cell_id"]]
            (
                pd.read_csv(dest_traces, skiprows=[1])
                .rename(columns={" ": "time"})
                .melt(id_vars="time", var_name="session_cell_id", value_name="value")
                .assign(
                    session_cell_id=lambda x: self.tidy_cell_ids(x.session_cell_id),
                    time=lambda x: np.round(x.time, 2),
                )
                .merge(master_cellset[["cell_id", "session_cell_id"]])
                .to_csv(dest_traces, index=False)
            )
            df_cell_props = (
                pd.read_csv(dest_props)
                .drop(
                    ["Status", "ColorR", "ColorG", "ColorB", "ActiveSegment0"], axis=1
                )
                .rename(
                    columns={
                        "Name": "session_cell_id",
                        "SNR": "snr",
                        "EventRate(Hz)": "event_rate",
                    }
                )
                .assign(session_cell_id=lambda x: self.tidy_cell_ids(x.session_cell_id))
                .merge(master_cellset)
            )
            df_cell_props.to_csv(dest_props, index=False)

    def export_spikes(
        self, src: Path, dest: Path, factor: float = 3, update_cellids: bool = True
    ) -> None:
        isx_events = tempfile.mktemp() + ".isxd"
        isx.event_detection(str(src), isx_events, threshold=factor)
        isx.export_event_set_to_csv(isx_events, str(dest))

        if update_cellids:
            master_cellset = pd.read_csv(self.logreg_file)
            master_cellset = master_cellset.loc[
                lambda x: x.session_index == self.session_index
            ]
            master_cellset = master_cellset[["cell_id", "session_cell_id"]]
            (
                pd.read_csv(dest)
                .rename(columns={"Time (s)": "time"})
                .melt(id_vars="time", var_name="session_cell_id", value_name="value")
                .assign(
                    session_cell_id=lambda x: self.tidy_cell_ids(x.session_cell_id),
                    time=lambda x: np.round(x.time, 2),
                )
                .merge(master_cellset[["cell_id", "session_cell_id"]])
                .to_csv(dest, index=False)
            )


def get_excluded_session_index(session_name: str, cohort: Cohort):
    if cohort == Cohort.PFC:
        sessions = [
            "day1-epm",
            "day2-morning",
            "day2-afternoon",
            "day3-morning",
            "day3-afternoon",
            "day4-test1",
            "day5-test2",
        ]
    elif cohort == Cohort.OFLNEW:
        sessions = ["day1", "day2", "day3", "day4"]
    else:
        raise ValueError("Unknown Cohort")
    return sessions.index(session_name)


def export(
    mouse_path: Path,
    cohort: Cohort,
    output_root_dir: Path,
    excluded_sessions: Optional[List[str]] = None,
):
    # find files
    if excluded_sessions is None:
        excluded_sessions = []
    session_dirs = SessionDirsFinder(mouse_path, cohort).find()
    raw_data_paths: Dict[str, SessionData] = OrderedDict()
    exported_data_paths: Dict[str, ExportPaths] = OrderedDict()
    for session_name, session_path in session_dirs.items():
        if session_name in excluded_sessions:
            print(f"{session_name}: - excluded")
            continue
        print(f"{session_name}: not-excluded")
        raw_data_paths[session_name] = FileFinder(session_path, cohort).find()
        exported_data_paths[session_name] = ExportFileFinder(
            session_name,
            mouse_path=mouse_path,
            output_root_dir=output_root_dir,
            cohort=cohort,
            unlink=True,
        ).find()
    # long reg
    cellsets: List[str] = [str(data.cellset_file) for data in raw_data_paths.values()]
    excluded_sessions_indexes = [
        get_excluded_session_index(sesh, cohort) for sesh in excluded_sessions
    ]
    logreg_file = longreg(
        cellsets,
        output_dir=output_root_dir / mouse_path.name,
        delete_if_exists=True,
        excluded_sessions_indexes=excluded_sessions_indexes,
    )

    # export traces and gpio
    for session_name in session_dirs.keys():
        session_index = get_excluded_session_index(session_name, cohort)
        if session_name in excluded_sessions:
            continue
        raw_data = raw_data_paths[session_name]
        exported_data = exported_data_paths[session_name]
        exporter = ISXFileExporter(logreg_file=logreg_file, session_index=session_index)
        exporter.export_traces(
            src=raw_data.cellset_file,
            dest_traces=exported_data.traces,
            dest_props=exported_data.trace_props,
            dest_tiff=exported_data.tiff,
        )
        exporter.export_spikes(
            src=raw_data.cellset_file, dest=exported_data.spikes, factor=3
        )
