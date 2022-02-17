from pathlib import Path
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
import isx
import logging
from .utils import _rmtree, tidy_cell_ids
import tempfile
from .data_obj import Mouse, Session


def longitudinal_registration(
    mouse: Mouse,
    csv_filename: str = "logreg_master.csv",
    acceped_cells_only: bool = True,
    delete_if_exist: bool = True,
) -> pd.DataFrame:
    if mouse.sessions is None:
        raise ValueError("Mouse has no sessions")
    if mouse.output_dir is None:
        raise ValueError("Mouse output directory not set")

    mouse.logreg_csv_file = mouse.output_dir / csv_filename
    cellsets = tuple(map(lambda x: x.cell_set, mouse.sessions))
    input_cellsets: List[str] = []
    output_cellsets: List[str] = []
    for session in mouse.sessions:
        cellset = session.cell_set
        if cellset is None:
            raise ValueError("Cellset is None")
        else:
            input_cellsets.append(str(cellset))
            output_cellset_fn = cellset.name + "tmp" + cellset.suffix
            output_cellset = cellset.parent / output_cellset_fn
            output_cellsets.append(str(output_cellset))
    if delete_if_exist:
        for p in list(map(Path, output_cellsets)) + [mouse.logreg_csv_file]:
            if p.exists():
                p.unlink()
    isx.longitudinal_registration(
        input_cellsets,
        output_cellsets,
        csv_file=str(mouse.logreg_csv_file),
        accepted_cells_only=acceped_cells_only,
    )

    for p in map(Path, output_cellsets):
        p.unlink()
    df = pd.read_csv(mouse.logreg_csv_file).rename(
        columns={
            "global_cell_index": "cell_id",
            "local_cell_index": "session_cell_id",
            "local_cellset_index": "session_index",
        }
    )

    df.to_csv(mouse.logreg_csv_file, index=False)
    return df


def export_gpios(mouse: Mouse) -> None:
    if mouse.sessions is None:
        raise ValueError("Mouse has no sessions")
    for session in mouse.sessions:
        export_gpio(session)


def export_traces(mouse: Mouse) -> None:
    if mouse.sessions is None:
        raise ValueError()
    for session in mouse.sessions:
        if session is None:
            raise ValueError()
    for session in mouse.sessions:
        export_trace(session)


def export_events(mouse: Mouse) -> None:
    if mouse.sessions is None:
        raise ValueError()
    for session in mouse.sessions:
        if session is None:
            raise ValueError()
    for session in mouse.sessions:
        export_event(session)


def export_trace(session: Session) -> None:
    if session.output_dir is None:
        raise ValueError()
    session.exported_trace_file = session.output_dir / "traces.csv"
    tiff_base_path = str(session.output_images_dir / "cell_image.tiff")
    session.trace_props_file = session.output_dir / "trace_props.csv"
    isx.export_cell_set_to_csv_tiff(
        input_cell_set_files=str(session.cell_set),
        output_csv_file=str(session.exported_trace_file),
        output_tiff_file=tiff_base_path,
        output_props_file=str(session.trace_props_file),
    )


def export_gpio(session: Session) -> None:
    if session.output_dir is None:
        raise ValueError("Session has no output directory")
    session.exported_gpio_file = session.output_dir / "gpio.csv"
    isx.export_gpio_set_to_csv(
        str(session.gpio_file),
        str(session.exported_gpio_file),
        inter_isxd_file_dir=tempfile.gettempdir(),
    )


def export_event(session: Session) -> None:
    if session.output_dir is None:
        raise ValueError()
    session.exported_events_file = session.output_dir / "events.csv"
    session.event_props_file = session.output_dir / "event_props.csv"
    isx.export_event_set_to_csv(
        input_event_set_files=str(session.event_file),
        output_csv_file=str(session.exported_events_file),
        output_props_file=str(session.event_props_file),
    )


def update_cell_props(
    session: Session, master_cellset: pd.DataFrame, unlink: bool = True
) -> pd.DataFrame:
    if session.trace_props_file is None:
        raise ValueError()
    if session.event_props_file is None:
        raise ValueError()

    df_cell_props = pd.read_csv(session.trace_props_file).loc[
        lambda x: x.Status == "accepted"
    ]
    df_event_props = pd.read_csv(session.event_props_file)
    df_cell_props = (
        pd.merge(df_cell_props, df_cell_props)
        .drop(["Status", "ColorR", "ColorG", "ColorB", "ActiveSegment0"], axis=1)
        .rename(
            columns={
                "Name": "session_cell_id",
                "SNR": "snr",
                "EventRate(Hz)": "event_rate",
            }
        )
        .assign(session_cell_id=lambda x: tidy_cell_ids(x.session_cell_id))
        .merge(master_cellset)
    )
    df_cell_props.to_csv(
        session.trace_props_file.parent / "cell_props.csv", index=False
    )
    if unlink:
        session.event_props_file.unlink()
        session.trace_props_file.unlink()

    return df_cell_props


def update_events(session: Session, master_cellset: pd.DataFrame) -> None:
    (
        pd.read_csv(session.exported_events_file)
        .rename(columns={"Time (s)": "time"})
        .melt(id_vars="time", var_name="session_cell_id", value_name="value")
        .assign(
            session_cell_id=lambda x: tidy_cell_ids(x.session_cell_id),
            time=lambda x: np.round(x.time, 2),
        )
        .merge(master_cellset[["cell_id", "session_cell_id"]])
        .to_csv(session.exported_events_file, index=False)
    )


def update_traces(session: Session, master_cellset: pd.DataFrame) -> None:
    (
        pd.read_csv(session.exported_trace_file, skiprows=[1])
        .rename(columns={" ": "time"})
        .melt(id_vars="time", var_name="session_cell_id", value_name="value")
        .assign(
            session_cell_id=lambda x: tidy_cell_ids(x.session_cell_id),
            time=lambda x: np.round(x.time, 2),
        )
        .merge(master_cellset[["cell_id", "session_cell_id"]])
        .to_csv(session.exported_trace_file, index=False)
    )


def update_session_cell_ids(session: Session, master_cellset: pd.DataFrame) -> None:
    update_cell_props(session=session, master_cellset=master_cellset)
    update_events(session=session, master_cellset=master_cellset)
    update_traces(session=session, master_cellset=master_cellset)


def update_cell_ids(mouse: Mouse, master_cellset: pd.DataFrame) -> None:
    if mouse.sessions is None:
        raise ValueError()
    for session in mouse.sessions:
        if session is None:
            raise ValueError()
        if session.session_index is None:
            raise ValueError()
    for session in mouse.sessions:
        master_cellset_session = master_cellset.loc[
            lambda x: x.session_index == session.session_index
        ]
        update_session_cell_ids(session, master_cellset=master_cellset_session)


def export_motion(mouse: Mouse) -> None:
    # TODO
    raise NotImplementedError()
