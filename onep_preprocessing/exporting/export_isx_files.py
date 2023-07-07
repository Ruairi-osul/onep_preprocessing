import isx
from typing import Optional
from pathlib import Path


class IsxExporter:
    def __init__(
        self,
        trace_filename: str = "traces.csv",
        props_filename: str = "properties.csv",
        tiff_subdir: Optional[str] = "tiff",
        tiff_filename: str = "cell_",
        on_exists: str = "overwrite",
    ):
        self.trace_filename = trace_filename
        self.props_filename = props_filename
        self.tiff_subdir = tiff_subdir
        self.tiff_filename = tiff_filename
        self.on_exists = on_exists

    def if_exists(self, file: Path):
        if file.exists():
            if self.on_exists == "overwrite":
                file.unlink()
            elif self.on_exists == "raise":
                raise FileExistsError(f"{file} already exists")
            elif self.on_exists == "skip":
                return True

    def __call__(self, cellset_file: Path, output_dir: Path):
        trace_file = output_dir / self.trace_filename
        props_file = output_dir / self.props_filename
        if self.tiff_subdir:
            tiff_file = output_dir / self.tiff_subdir / self.tiff_filename
            tiff_file.parent.mkdir(exist_ok=True)
        else:
            tiff_file = output_dir / self.tiff_filename

        self.if_exists(trace_file)
        self.if_exists(props_file)
        self.if_exists(tiff_file)

        isx.export_cell_set_to_csv_tiff(
            input_cell_set_files=[str(cellset_file)],
            output_csv_file=str(trace_file),
            output_props_file=str(props_file),
            output_tiff_file=str(tiff_file),
        )
