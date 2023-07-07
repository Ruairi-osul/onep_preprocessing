import isx
from typing import Sequence, Optional, Union
from pathlib import Path
import tempfile


class IsxLongtitudinalRegistration:
    def __init__(
        self,
        min_correlation: float = 0.5,
        accepted_cells_only: bool = True,
        on_exists: str = "overwrite",
    ):
        self.min_correlation = min_correlation
        self.on_exists = on_exists
        self.accepted_cells_only = accepted_cells_only

    def _gen_temp_cellsets(self, cellset_files: Sequence[Path]) -> Sequence[Path]:
        tmp_dir = Path(tempfile.gettempdir())
        output_cellsets = [
            tmp_dir / (str(i) + Path(f).name) for i, f in enumerate(cellset_files)
        ]
        return output_cellsets

    def if_exists(self, file: Path):
        if file.exists():
            if self.on_exists == "overwrite":
                file.unlink()
            elif self.on_exists == "raise":
                raise FileExistsError(f"{file} already exists")
            elif self.on_exists == "skip":
                return True

    def __call__(
        self,
        cellset_files: Sequence[Path],
        output_csv_file: Path,
        transform_csv_file: Optional[Union[Path, str]] = None,
        crop_csv_file: Optional[Union[Path, str]] = None,
    ):
        self.if_exists(Path(output_csv_file))
        temp_cellsets = self._gen_temp_cellsets(cellset_files)

        if transform_csv_file:
            self.if_exists(Path(transform_csv_file))
        else:
            transform_csv_file = ""

        if crop_csv_file:
            self.if_exists(Path(crop_csv_file))
        else:
            crop_csv_file = ""


        isx.longitudinal_registration(
            input_cell_set_files=[str(f) for f in cellset_files],
            output_cell_set_files=[str(f) for f in temp_cellsets],
            csv_file=str(output_csv_file),
            transform_csv_file=str(transform_csv_file),
            crop_csv_file=str(crop_csv_file),
            min_correlation=self.min_correlation,
            accepted_cells_only=self.accepted_cells_only,
        )
