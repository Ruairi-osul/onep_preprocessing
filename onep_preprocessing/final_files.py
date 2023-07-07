from typing import List
from pathlib import Path
import pandas as pd

INPATH = Path(r"E:\Context\PFC - Cohort 1\1p Export")
OUTPUTDIR = Path(r"F:\Context\pfc_new")
SESSIONS = [
    "day1-epm",
    "day2-morning",
    "day2-afternoon",
    "day3-morning",
    "day3-afternoon",
    "day4-test1",
    "day5-test2",
]


def find_traces(session_dir: Path) -> Path:
    """Find Trace File from Session Dir

    Args:
        session_dir (Path): Path to Session Dir

    Raises:
        FileNotFoundError: If not Found

    Returns:
        Path: Path to Trace Files
    """
    trace_file = session_dir / "traces.csv"
    if not trace_file.exists():
        print(str(trace_file))
        raise FileNotFoundError("No Trace File.")
    return trace_file


def find_spikes(session_dir: Path) -> Path:
    """Find Spikes file from session dir

    Args:
        session_dir (Path): Path to Session Dir

    Raises:
        FileNotFoundError: If not Found

    Returns:
        Path: Path to Spikes File
    """
    spikes_file = session_dir / "spikes.csv"
    if not spikes_file.exists():
        raise FileNotFoundError("No Spikes File.")
    return spikes_file


def find_logreg_file(mouse_dir: Path) -> Path:
    """Find Logreg file from mouse dir

    Args:
        mouse_dir (Path): Mouse dir

    Raises:
        FileNotFoundError: If not Found

    Returns:
        Path: Path to Logreg File
    """
    logreg_file = mouse_dir / "logreg_file.csv"
    if not logreg_file.exists():
        raise FileNotFoundError("No Logreg File")
    return logreg_file


def get_mouse_dirs(root_dir: Path) -> List[Path]:
    """Get mouse dirs from root dir

    Args:
        root_dir (Path): Root Dir

    Returns:
        List[Path]: List of Session Dirs
    """
    return [d for d in root_dir.glob("*") if d.is_dir()]


def get_mouse_sessions(mouse_dir: Path) -> List[Path]:
    """Get session dirs from mouse dir

    Args:
        mouse_dir (Path): Path to mouse dir

    Returns:
        List[Path]: List of session dir objects
    """
    return [d for d in mouse_dir.glob("*") if d.is_dir() and d.name in SESSIONS]


def main() -> None:
    logreg_files = []
    trace_paths = []
    spikes_paths = []
    mouse_dirs = get_mouse_dirs(INPATH)
    for mouse_dir in mouse_dirs:
        sessions = get_mouse_sessions(mouse_dir)
        logreg_files.append(find_logreg_file(mouse_dir))
        for session in sessions:
            try:
                trace_paths.append(find_traces(session))
                spikes_paths.append(find_spikes(session))
            except FileNotFoundError as e:
                print(f"{mouse_dir.name} - {session.name}")
                raise e

    cells_df = pd.concat([pd.read_csv(p) for p in logreg_files])
    cells_df.to_parquet(
        OUTPUTDIR / "cells.parquet.gzip", index=False, compression="gzip"
    )

    for session_name in SESSIONS:
        session_output_dir = OUTPUTDIR / session_name
        session_output_dir.mkdir(parents=True, exist_ok=True)
        df_traces = pd.concat(
            [pd.read_csv(f) for f in trace_paths if f.parent.name == session_name]
        )
        df_traces.to_parquet(
            session_output_dir / f"traces-{session_name}.parquet.gzip",
            index=False,
            compression="gzip",
        )
        del df_traces

        df_spikes = pd.concat(
            [pd.read_csv(f) for f in spikes_paths if f.parent.name == session_name]
        )
        df_spikes.to_parquet(
            session_output_dir / f"spikes-{session_name}.parquet.gzip",
            index=False,
            compression="gzip",
        )


if __name__ == "__main__":
    main()
