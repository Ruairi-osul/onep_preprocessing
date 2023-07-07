from typing import Any, Union, Optional
from pathlib import Path
from .preprocessors import (
    ISXDownSampler,
    ISXSpatialFilterer,
    ISXMotionCorrector,
    ISXDff,
)
from .cnmfe import ISXCNMFe
import warnings


class Dispatcher:
    """

    Args:
        output_dir (Optional[Union[Path, str]], optional): Output directory, relative or absolute. Defaults to None.
        on_exists (str): What to do if the output file already exists {"overwrite", "raise", "skip"}. Defaults to "overwrite".
    """

    def __init__(self, output_dir, on_exists: str = "overwrite"):
        self.output_dir = output_dir
        self.on_exists = on_exists

    def _get_outputdir(self, input_dir: Path) -> Path:
        """Get the output directory for a given input directory.

        Args:
            input_dir (Path): Input directory.

        Returns:
            Path: Output directory.
        """
        if self.output_dir is None:
            return input_dir
        elif (
            isinstance(self.output_dir, str) and not Path(self.output_dir).is_absolute()
        ):
            return input_dir / self.output_dir
        else:
            return Path(self.output_dir)

    def file_exists(self, path: Path) -> bool:

        if path.exists():
            if self.on_exists == "overwrite":
                path.unlink()
            elif self.on_exists == "raise":
                raise FileExistsError(f"{path} already exists.")
            elif self.on_exists == "skip":
                warnings.warn(f"Skipping {path}, file already exists.")
                return True
            else:
                raise ValueError(f"Unknown on_exists value: {self.on_exists}")
        return False

    def __call__(self, isx_video: Path) -> Any:
        ...


class PreprocessorDispatcher(Dispatcher):
    def __init__(
        self,
        downsampler: ISXDownSampler,
        spatial_filterer: ISXSpatialFilterer,
        motion_corrector: ISXMotionCorrector,
        dff: ISXDff,
        output_dir: Optional[Union[Path, str]] = None,
        on_exists: str = "overwrite",
    ):
        """
        A class that dispatches preprocessing operations.

        Args:
            downsampler (ISXDownSampler): Downsampler.
            spatial_filterer (ISXSpatialFilterer): Spatial filterer.
            motion_corrector (ISXMotionCorrector): Motion corrector.
            dff (ISXDff): Dff.
            output_dir (Optional[Union[Path, str]], optional): Output directory, relative or absolute. Defaults to None.
            on_exists (str): What to do if the output file already exists {"overwrite", "raise", "skip"}. Defaults to "overwrite".
        """
        self.downsampler = downsampler
        self.spatial_filterer = spatial_filterer
        self.motion_corrector = motion_corrector
        self.dff = dff
        self.output_dir = output_dir
        self.on_exists = on_exists

    def __call__(self, isx_video: Path) -> Any:
        """Dispatch preprocessing operations.

        Args:
            isx_video (Path): Path to ISX video.

        Returns:
            Any: Output of the last preprocessing operation.
        """
        output_dir = self._get_outputdir(isx_video.parent)
        output_dir.mkdir(exist_ok=True, parents=True)

        # Downsample
        downsampler_output = output_dir / f"{isx_video.stem}_downsampled.isxd"
        if not self.file_exists(downsampler_output):
            self.downsampler(isx_video, downsampler_output)

        # Spatial filter
        spatial_filterer_output = output_dir / f"{isx_video.stem}_spatial_filtered.isxd"
        if not self.file_exists(spatial_filterer_output):
            self.spatial_filterer(downsampler_output, spatial_filterer_output)

        # Motion correct
        motion_corrector_output = output_dir / f"{isx_video.stem}_motion_corrected.isxd"
        if not self.file_exists(motion_corrector_output):
            self.motion_corrector(spatial_filterer_output, motion_corrector_output)

        # DFF
        dff_output = output_dir / f"{isx_video.stem}_dff.isxd"
        if not self.file_exists(dff_output):
            self.dff(motion_corrector_output, dff_output)

        return motion_corrector_output


class CNMFeDispatcher(Dispatcher):
    def __init__(
        self,
        cnmfe: ISXCNMFe,
        output_dir: Optional[Union[Path, str]] = None,
        on_exists: str = "overwrite",
    ):
        """
        A class that dispatches CNMFe operations.

        Args:
            cnmfe (ISXCNMFe): CNMFe.
            output_dir (Optional[Union[Path, str]], optional): Output directory, relative or absolute. Defaults to None.
            on_exists (str): What to do if the output file already exists {"overwrite", "raise", "skip"}. Defaults to "overwrite".
        """
        self.cnmfe = cnmfe
        self.output_dir = output_dir
        self.on_exists = on_exists

    def __call__(self, isx_video: Path) -> Any:
        """Dispatch CNMFe operations.

        Args:
            isx_video (Path): Path to ISX video.

        Returns:
            Any: Output of the last preprocessing operation.
        """
        output_dir = self._get_outputdir(isx_video.parent)
        output_dir.mkdir(exist_ok=True, parents=True)

        # CNMFe
        cnmfe_output = output_dir / f"{isx_video.stem}_cnmfe_cellset.isxd"
        if not self.file_exists(cnmfe_output):
            self.cnmfe(isx_video, cnmfe_output)

        return cnmfe_output
