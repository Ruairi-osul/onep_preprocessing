import isx
from typing import Any, Union
from pathlib import Path


class ISXPreprocessor:
    def __call__(self, in_vid: Path, out_vid: Path):
        raise NotImplementedError


class ISXDownSampler(ISXPreprocessor):
    def __init__(
        self,
        temporal_factor: float = 2,
        spatial_factor: float = 4,
        crop_rect: Union[Any, None] = None,
        fix_defective_pixels: bool = True,
        trim_early_frames: bool = True,
    ):
        """

        Args:
            temporal_factor (float, optional): Temporal downsample factor. Defaults to 2.
            spatial_factor (float, optional): Spatial downsample factor. Defaults to 4.
            crop_rect (Union[Any, None], optional): A list of 4 pixel locations that determines the crop rectangle: [top, left, bottom, right]. Defaults to None.
            fix_defective_pixels (bool, optional): Fix defective pixels. Defaults to True.
            trim_early_frames (bool, optional): Trim early frames. Defaults to True.
        """
        self.temporal_factor = temporal_factor
        self.spatial_factor = spatial_factor
        self.crop_rect = crop_rect
        self.fix_defective_pixels = fix_defective_pixels
        self.trim_early_frames = trim_early_frames

    def __call__(self, in_vid: Path, out_vid: Path):
        isx.preprocess(
            str(in_vid),
            str(out_vid),
            temporal_downsample_factor=self.temporal_factor,
            spatial_downsample_factor=self.spatial_factor,
            crop_rect=self.crop_rect,
            fix_defective_pixels=self.fix_defective_pixels,
            trim_early_frames=self.trim_early_frames,
        )


class ISXSpatialFilterer(ISXPreprocessor):
    def __init__(
        self,
        low_cutoff: float = 0.005,
        high_cutoff: float = 0.5,
        retain_mean: bool = False,
        subtract_global_minimum: bool = True,
    ):
        """

        Args:
            low_cutoff (float, optional): Low cutoff frequency. Defaults to 0.005.
            high_cutoff (float, optional): High cutoff frequency. Defaults to 0.5.
            retain_mean (bool, optional): Retain mean. Defaults to False.
            subtract_global_minimum (bool, optional): Subtract global minimum after frame by frame. By doing this, all pixel intensities will stay positive valued, and integer-valued movies can stay that way. Defaults to True.
        """
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff
        self.retain_mean = retain_mean
        self.subtract_global_minimum = subtract_global_minimum

    def __call__(self, in_vid: Path, out_vid: Path):
        isx.spatial_filter(
            str(in_vid),
            str(out_vid),
            low_cutoff=self.low_cutoff,
            high_cutoff=self.high_cutoff,
            retain_mean=self.retain_mean,
            subtract_global_minimum=self.subtract_global_minimum,
        )


class ISXMotionCorrector(ISXPreprocessor):
    def __init__(
        self,
        max_translation: float = 20,
        low_bandpass_cutoff: float = 0.054,
        high_bandpass_cutoff: float = 0.067,
        roi: Union[Any, None] = None,
        reference_segment_index: int = 0,
        reference_frame_index: int = 0,
        reference_file_name: str = "",
        global_registration_weight: float = 1,
        output_translation_files: Union[Any, None] = None,
        output_crop_rect_file: Union[Any, None] = None,
    ):
        """
        Args:
            max_translation (float, optional): Maximum translation in pixels. Defaults to 20.
            low_bandpass_cutoff (float, optional): Low bandpass cutoff frequency. Defaults to 0.004.
            high_bandpass_cutoff (float, optional): High bandpass cutoff frequency. Defaults to 0.016.
            roi (Union[Any, None], optional) If not None, each row is a vertex of the ROI to use for motion estimation. Otherwise, use the entire frame.
            reference_segment_index (int, optional):  If a reference frame is to be specified, this parameter indicates the index of the movie whose frame will be utilized, with respect to input_movie_files. If only one movie is specified to be motion corrected, this parameter must be 0.
            reference_frame_index (int, optional): Use this parameter to specify the index of the reference frame to be used, with respect to reference_segment_index. If reference_file_name is specified, this parameter, as well as reference_segment_index, is ignored.
            reference_file_name (str, optional): If an external reference frame is to be used, this parameter should be set to path of the .isxd file that contains the reference image.
            global_registration_weight (float, optional): When this is set to 1, only the reference frame is used for motion estimation. When this is less than 1, the previous frame is also used for motion estimation. The closer this value is to 0, the more the previous frame is used and the less the reference frame is used.
            output_translation_files (Any | None, optional):  A list of file names to write the X and Y translations to. Must be either None, in which case no files are written, or a list of valid file names equal in length to the number of input and output file names. The output translations are written into a .csv file with three columns. The first two columns, "translationX" and "translationY", store the X and Y translations from each frame to the reference frame respectively. The third column contains the time of the frame since the beginning of the movie. The first row stores the column names as a header. Each subsequent row contains the X translation, Y translation, and time offset for that frame.
            output_crop_rect_file (Any | None, optional): The path to a file that will contain the crop rectangle applied to the input movies to generate the output movies. The format of the crop rectangle is a comma separated list: x,y,width,height.
        """
        self.max_translation = max_translation
        self.low_bandpass_cutoff = low_bandpass_cutoff
        self.high_bandpass_cutoff = high_bandpass_cutoff
        self.roi = roi
        self.reference_segment_index = reference_segment_index
        self.reference_frame_index = reference_frame_index
        self.reference_file_name = reference_file_name
        self.global_registration_weight = global_registration_weight
        self.output_translation_files = output_translation_files
        self.output_crop_rect_file = output_crop_rect_file

    def __call__(self, in_vid: Path, out_vid: Path):
        isx.motion_correct(
            str(in_vid),
            str(out_vid),
            max_translation=self.max_translation,
            low_bandpass_cutoff=self.low_bandpass_cutoff,
            global_registration_weight=self.global_registration_weight,
            high_bandpass_cutoff=self.high_bandpass_cutoff,
            roi=self.roi,
            reference_segment_index=self.reference_segment_index,
            reference_frame_index=self.reference_frame_index,
            reference_file_name=self.reference_file_name,
            output_translation_files=self.output_translation_files,
            output_crop_rect_file=self.output_crop_rect_file,
            
        )


class ISXDff(ISXPreprocessor):
    def __init__(
        self,
        f0_type: str = "mean",
    ):
        """

        Args:
            f0_type (str, optional): Type of F0 to use {'mean', 'min'}. Defaults to "mean".
        """
        self.f0_type = f0_type

    def __call__(self, in_vid: Path, out_vid: Path):
        isx.dff(
            str(in_vid),
            str(out_vid),
            f0_type=self.f0_type,
        )


    