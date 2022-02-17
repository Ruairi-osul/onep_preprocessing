from typing import Optional, List, Tuple
from pathlib import Path
from .utils import _rmtree


class Session:
    def __init__(
        self,
        name: str,
        cell_set: Optional[Path] = None,
        event_file: Optional[Path] = None,
        gpio_file: Optional[Path] = None,
        session_index: Optional[int] = None,
        output_dir: Optional[Path] = None,
        exported_trace_file: Optional[Path] = None,
        exported_events_file: Optional[Path] = None,
        exported_props_file: Optional[Path] = None,
        exported_gpio_file: Optional[Path] = None,
        trace_props_file: Optional[Path] = None,
        events_props_file: Optional[Path] = None,
    ):
        self.name = name
        self.cell_set = cell_set
        self.event_file = event_file
        self.session_index = session_index
        self.gpio_file = gpio_file
        self.output_dir = output_dir
        if self.output_dir is not None:
            self.output_images_dir = self.output_dir / "images"
            self._mkdirs()
        self.exported_trace_file = exported_trace_file
        self.exported_events_file = exported_events_file
        self.exported_props_file = exported_props_file
        self.exported_gpio_file = gpio_file
        self.trace_props_file = trace_props_file
        self.event_props_file = events_props_file

    def _mkdirs(self) -> None:
        dirs = (self.output_dir, self.output_images_dir)
        for d in dirs:
            if d is not None:
                d.mkdir(exist_ok=True, parents=True)

    def delete_existing_exports(self) -> None:
        if self.output_dir is None:
            raise ValueError("No output dir specified")
        _rmtree(self.output_dir)
        for p in [
            self.output_dir,
            self.output_images_dir,
        ]:
            p.mkdir()

    @classmethod
    def from_config_dict(cls, d: dict, index: int, output_dir: Path = None):
        return cls(
            name=d["name"],
            cell_set=Path(d["cell set"]),
            event_file=Path(d["event file"]),
            session_index=index,
            output_dir=output_dir,
            gpio_file=Path(d["gpio file"]),
        )

    @classmethod
    def from_dir(cls, p: Path, updated: bool = True):
        session_name = p.name
        output_dir = p
        exported_trace_file = p / "traces.csv"
        exported_events_file = p / "events.csv"
        trace_props_file = p / "trace_props.csv"
        event_props_file = p / "event_props.csv"
        gpio_file = p / "gpio.csv"
        if updated:
            exported_props_file: Optional[Path] = p / "cell_props.csv"
        else:
            exported_props_file = None
        return cls(
            name=session_name,
            output_dir=output_dir,
            exported_trace_file=exported_trace_file,
            exported_events_file=exported_events_file,
            exported_props_file=exported_props_file,
            trace_props_file=trace_props_file,
            events_props_file=event_props_file,
        )

    def __repr__(self):
        return f"<Session: {self.name}>"


class Mouse:
    def __init__(
        self,
        name: str,
        sessions: Optional[Tuple[Session, ...]] = None,
        output_dir: Optional[Path] = None,
        logreg_csv_file: Optional[Path] = None,
    ):
        self.name: str = name
        self.output_dir = output_dir
        if self.output_dir is not None:
            self.output_dir.mkdir(exist_ok=True)

        self.sessions = sessions
        self.logreg_csv_file = logreg_csv_file

    def delete_existing_exports(self) -> None:
        if self.output_dir is None:
            raise ValueError()
        _rmtree(self.output_dir)
        self.output_dir.mkdir()
        if self.sessions:
            for session in self.sessions:
                if session:
                    session._mkdirs()

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    @classmethod
    def from_dir(cls, p: Path):
        sessions = tuple(Session.from_dir(x) for x in p.glob("*") if x.is_dir())
        logreg_file = (
            p / "logreg_master.csv" if (p / "logreg_master.csv").exists() else None
        )
        return Mouse(name=p.name, sessions=sessions, logreg_csv_file=logreg_file)

    @classmethod
    def from_config_dict(cls, d: dict, master_output_dir: Path):
        name = d["name"]
        output_dir = master_output_dir / name
        sessions = [
            Session.from_config_dict(
                d_, index=i, output_dir=output_dir.joinpath(d_["name"])
            )
            for i, d_ in enumerate(d["sessions"])
        ]
        return cls(name=name, sessions=tuple(sessions), output_dir=output_dir)

    def __repr__(self):
        return f"<Mouse: {self.name}>"
