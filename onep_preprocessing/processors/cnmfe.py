from typing import Any
import isx
from pathlib import Path


class ISXCellFinder:
    def __call__(self, in_vid: Path, out_cellset: Path) -> Any:
        ...


class ISXCNMFe(ISXCellFinder):
    def __init__(
        self,
        cell_diameter: int = 7,
        min_corr: float = 0.8,
        min_pnr: int = 10,
        bg_spatial_subsampling: int = 2,
        ring_size_factor: float = 1.4,
        gaussian_kernel_size: int = 0,
        closing_kernel_size: int = 0,
        merge_threshold: float = 0.7,
        processing_mode: str = "parallel_patches",
        num_threads: int = 4,
        patch_size: int = 80,
        patch_overlap: int = 20,
        output_unit_type: str = "df_over_noise",
    ):
        """

        Args:
            cell_diameter (int, optional): Expected average diameter of a neuron in pixels. Defaults to 7.
            min_corr (float, optional): Minimum correlation with neighbours when searching for seed pixels. Defaults to 0.8.
            min_pnr (int, optional): Minimum peak-to-noise ratio when searching for seed pixels. Defaults to 10.
            bg_spatial_subsampling (int, optional): Background spatial downsampling factor. Defaults to 2.
            ring_size_factor (float, optional): Ratio of ring radius to neuron diameter used for estimating background. Defaults to 1.4.
            gaussian_kernel_size (int, optional): Width of Gaussian kernel to use for spatial filtering. Defaults to 0.
            closing_kernel_size (int, optional): Morphological closing kernel size. Defaults to 0.
            merge_threshold (float, optional): Temporal correlation threshold for merging spatially close cells. Defaults to 0.7.
            processing_mode (str, optional): Processing mode for Cnmfe  {'all_in_memory', 'sequential_patches', 'parallel_patches'}. Defaults to "parallel_patches".
            num_threads (int, optional): Number of threads to use for processing the data. Defaults to 4.
            patch_size (int, optional): Size of the patches to process. Defaults to 80.
            patch_overlap (int, optional): Overlap between patches. Defaults to 20.
            output_unit_type (str, optional): Output unit type. Defaults to "df_over_noise".
        """
        self.cell_diameter = cell_diameter
        self.min_corr = min_corr
        self.min_pnr = min_pnr
        self.bg_spatial_subsampling = bg_spatial_subsampling
        self.ring_size_factor = ring_size_factor
        self.gaussian_kernel_size = gaussian_kernel_size
        self.closing_kernel_size = closing_kernel_size
        self.merge_threshold = merge_threshold
        self.processing_mode = processing_mode
        self.num_threads = num_threads
        self.patch_size = patch_size
        self.patch_overlap = patch_overlap
        self.output_unit_type = output_unit_type

    def __call__(self, in_vid: Path, out_cellset: Path) -> Any:
        tmp_dir = out_cellset.parent / "cnmfe_tmp_files"
        tmp_dir.mkdir(exist_ok=True)
        isx.run_cnmfe(
            [str(in_vid)],
            [str(out_cellset)],
            output_dir=str(tmp_dir),
            cell_diameter=self.cell_diameter,
            min_corr=self.min_corr,
            min_pnr=self.min_pnr,
            bg_spatial_subsampling=self.bg_spatial_subsampling,
            ring_size_factor=self.ring_size_factor,
            gaussian_kernel_size=self.gaussian_kernel_size,
            closing_kernel_size=self.closing_kernel_size,
            merge_threshold=self.merge_threshold,
            processing_mode=self.processing_mode,
            num_threads=self.num_threads,
            patch_size=self.patch_size,
            patch_overlap=self.patch_overlap,
            output_unit_type=self.output_unit_type,
        )
