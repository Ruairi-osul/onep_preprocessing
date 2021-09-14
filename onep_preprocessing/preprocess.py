from pathlib import Path
from typing import List, Optional, Dict
import isx


def preprocess(in_path: Path, out_dir: Optional[Path] = None):
    """Preprocess a single insopix video

    Args:
        in_path (Path): Path to inscopix .isxd file
        out_dir (Optional[Path], optional): Path where files will be saved. Defaults to directory of input video.
    """

    def _generate_default_outpath(inpath: Path) -> Path:
        return inpath.parent

    def _create_paths(in_path: Path, out_path: Path) -> Dict[str, Path]:
        out = {}
        out["downsample_path"] = out_path / "downsampled.isxd"
        out["spatial_filter_path"] = out_path / "spatial_filtered.isxd"
        out["motion_correct_path"] = out_path / "motion_corrected.isxd"
        out["cnmfe_path"] = out_path / "cnmfe_cellset.isxd"
        for path in out.values():
            if path.exists():
                path.unlink()
        return out

    def _downsample(
        in_vid: Path,
        out_vid: Path,
        temporal_factor: float = 2,
        spatial_factor: float = 4,
    ):
        print("downsampling...")
        isx.preprocess(
            str(in_vid),
            str(out_vid),
            temporal_downsample_factor=temporal_factor,
            spatial_downsample_factor=spatial_factor,
        )

    def _spatial_filter(
        in_vid: Path, out_vid: Path, low_cutoff: float = 0.005, high_cutoff: float = 0.5
    ):
        print("applying spatial filter...")
        isx.spatial_filter(
            str(in_vid), str(out_vid), low_cutoff=low_cutoff, high_cutoff=high_cutoff
        )

    def _motion_correct(
        in_vid: Path,
        out_vid: Path,
        max_translation: int = 20,
        low_bandpass_cutoff: float = 0.054,
        high_bandpass_cutoff=0.067,
    ):
        print("motion correcting...")
        out_motion = out_vid.parent / "motion_ts.csv"
        isx.motion_correct(
            str(in_vid),
            str(out_vid),
            max_translation=max_translation,
            low_bandpass_cutoff=low_bandpass_cutoff,
            high_bandpass_cutoff=high_bandpass_cutoff,
            output_translation_files=str(out_motion),
        )

    def _cnmfe(in_vid: Path, out_dir: Path, num_threads: int = 5):
        print("running cnmfe")
        isx.run_cnmfe(
            input_movie_files=[str(in_vid)],
            output_cell_set_files=[str(out_dir)],
            output_dir=str(out_dir.parent),
            num_threads=num_threads,
        )

    if out_dir is None:
        out_dir = _generate_default_outpath(in_path)

    out_paths = _create_paths(in_path=in_path, out_path=out_dir)
    _downsample(in_path, out_paths["downsample_path"])
    _spatial_filter(out_paths["downsample_path"], out_paths["spatial_filter_path"])
    _motion_correct(out_paths["spatial_filter_path"], out_paths["motion_correct_path"])
    _cnmfe(out_paths["motion_correct_path"], out_paths["cnmfe_path"])
