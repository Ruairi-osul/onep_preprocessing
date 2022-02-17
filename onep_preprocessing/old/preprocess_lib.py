from typing import List, Tuple
import isx
from pathlib import Path
from .utils import _make_outpath


def downsample(
    in_vid: Path, temperal_factor: int = 2, spatial_factor: int = 4,
) -> Path:
    out_vid = _make_outpath(in_vid, operation_name="downsample", subdir="processed")
    isx.preprocess(
        str(in_vid),
        str(out_vid),
        temporal_downsample_factor=temperal_factor,
        spatial_downsample_factor=spatial_factor,
    )
    return out_vid


def spatial_filter(
    in_vid: Path, low_cutoff: float = 0.005, high_cutoff: float = 0.500
) -> Path:
    out_vid = _make_outpath(in_vid, operation_name="spatial_filter")
    isx.spatial_filter(
        str(in_vid), str(out_vid), low_cutoff=low_cutoff, high_cutoff=high_cutoff
    )
    return out_vid


def motion_correct(
    in_vid: Path,
    max_translation: int = 20,
    low_bandpass_cutoff: float = 0.040,
    high_bandpass_cutoff=0.067,
    reference_frame_index: int = 0,
    global_registration_weight: float = 0.8,
) -> Tuple[Path, Path]:
    out_vid = _make_outpath(in_vid, operation_name="motion_correct")
    out_motion = _make_outpath(in_vid, operation_name="motion_ts", suffix=".csv")

    isx.motion_correct(
        str(in_vid),
        str(out_vid),
        max_translation=max_translation,
        low_bandpass_cutoff=low_bandpass_cutoff,
        high_bandpass_cutoff=high_bandpass_cutoff,
        reference_frame_index=0,
        global_registration_weight=0.8,
        output_translation_files=str(out_motion),
    )
    return out_vid, out_motion

