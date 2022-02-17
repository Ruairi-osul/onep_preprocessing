from .utils import _make_outpath
from pathlib import Path
from typing import Tuple, List
import isx


def _remove_tiff(in_vid: Path) -> None:
    tiff_file = in_vid.parent / (in_vid.stem + ".tiff")
    if tiff_file.exists():
        tiff_file.unlink()


def cnmfe(
    in_vid: Path,
    num_processes: int = 10,
    overwrite_tiff: bool = True,
    K: int = 20,
    rf: List[int] = [25, 25],
    stride: int = 6,
    gSiz: int = 13,
    gSig: int = 5,
    min_pnr: float = 5,
    min_corr: float = 0.8,
    min_SNR: float = 5,
    rval_thr: float = 0.85,
    decay_time: float = 0.400,
    event_threshold: float = 0.025,
    merge_threshold: float = 0.8,
) -> Tuple[Path, Path]:
    cell_set_file = _make_outpath(
        in_vid, operation_name="cnmfe_cell_set", subdir="cnmfe"
    )
    events_file = _make_outpath(in_vid, operation_name="cnmfe_events", subdir="cnmfe")
    if overwrite_tiff:
        _remove_tiff(in_vid)
    isx.run_cnmfe(
        input_movie_files=str(in_vid),
        output_cell_set_files=str(cell_set_file),
        output_events_files=str(events_file),
        num_processes=num_processes,
        overwrite_tiff=overwrite_tiff,
        K=K,
        rf=rf,
        stride=stride,
        gSiz=gSiz,
        gSig=gSig,
        min_pnr=min_pnr,
        min_corr=min_corr,
        ssub_B=1,
        min_SNR=min_SNR,
        rval_thr=rval_thr,
        decay_time=decay_time,
        event_threshold=event_threshold,
        merge_threshold=merge_threshold,
        output_dir=None,
    )
    return cell_set_file, events_file
