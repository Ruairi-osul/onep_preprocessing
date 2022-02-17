from pathlib import Path
import numpy as np
import pandas as pd
from typing import Optional, Tuple, Iterable, Any


def _rmtree(root: Path) -> None:
    for p in root.iterdir():
        if p.is_dir():
            _rmtree(p)
        elif p.is_file:
            p.unlink()
        elif p.is_dir:
            p.rmdir()
    root.rmdir()


def tidy_cell_ids(ser: pd.Series) -> pd.Series:
    return ser.apply(lambda x: int(x.split("C")[1]))


def ticks(
    current: np.ndarray,
    desired_min: float,
    desired_max: float,
    num_ticks: int,
    lims: Optional[Tuple[float, float]] = None,
    round_digits: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Get ticks and corresponding ticklabels for plotting

    Args:
        current (np.array): The current ticks
        desired_max (float): The maximum tick
        desired_min (float): The minimum tick
        num_ticks (int): The number of ticks

    Returns:
        Tuple[np.array, np.array]: ticks, labels
    """
    if lims is not None:
        lower, upper = lims
        current = current[current >= lower]
        current = current[current <= upper]
    ticks = np.linspace(np.min(current), np.max(current), num_ticks, endpoint=True)
    labels = np.linspace(desired_min, desired_max, num_ticks, endpoint=True)
    if round_digits is not None:
        labels = np.round(labels, round_digits)
    return ticks, labels


def create_combined_col(
    df: pd.DataFrame, c1: str, c2: str, returned_colname: Optional[str] = None
) -> pd.DataFrame:
    if returned_colname is None:
        returned_colname = f"{c1}_{c2}"
    return df.assign(
        **{
            returned_colname: lambda x: x[c1]
            .astype(str)
            .str.cat(x[c2].astype(str), sep="_")
        }
    )


def _make_outpath(
    in_path: Path,
    operation_name: str,
    suffix: str = None,
    subdir: str = "",
    replace=True,
) -> Path:
    """Generates a file path"""
    if suffix is None:
        suffix = in_path.suffix
    outpath_name = "".join([in_path.stem, "_", operation_name, suffix])
    out_dir = in_path.parent / subdir
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / outpath_name
    if replace:
        _delete_if_exists(out_path)
    return out_path


def _delete_if_exists(p: Path) -> None:
    if p.exists():
        p.unlink()
