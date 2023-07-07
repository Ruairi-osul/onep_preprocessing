from typing import Iterable, List, Dict
import pandas as pd
from enum import Enum, auto
from pathlib import Path
import re


class Cohort(Enum):
    OFL = auto()
    PFC = auto()


class MouseDirFinder:
    def __init__(self, root_dir: Path, cohort: Cohort):
        self.path = root_dir
        self._find_method = self._find_method_fac(cohort)

    def _find_method_fac(self, cohort: Cohort):
        if cohort is Cohort.OFL:
            return self._find_ofl

    def _find_ofl(self) -> List[Path]:
        return [d for d in self.path.glob("*") if d.is_dir()]

    def _find_pfc(self) -> List[Path]:
        return self._find_ofl()

    def find(self) -> List[Path]:
        return self._find_ofl()


class FileFinder:
    def __init__(self, processed_data_dir: Path, cohort: Cohort):
        self.path = processed_data_dir
        self._find_method = self._finder_fac(cohort)

    def _finder_fac(self, cohort: Cohort):
        if cohort is Cohort.OFL:
            return self._finder_ofl
        elif cohort is Cohort.PFC:
            return self._finder_pfc

    def _finder_ofl(
        self,
    ) -> Dict[str, List[Path]]:
        all_files = list(self.path.rglob("*"))
        d = {}
        d["logreg_files"] = [f for f in all_files if re.search("logreg", f.name)]
        d["spikes_files"] = [
            f
            for f in all_files
            if re.search("events", f.name) or re.search("spikes", f.name)
        ]
        d["trace_files"] = [f for f in all_files if re.search("traces", f.name)]
        return d

    def _finder_pfc(self) -> Dict[str, List[Path]]:
        return self._finder_ofl()

    def find(self) -> Dict[str, List[Path]]:
        return self._find_method()


class IDUpdater:
    @staticmethod
    def update_logreg(logreg_paths: Dict[str, Path]) -> None:
        logreg_files: List[pd.DataFrame] = []
        for mouse_name, p in logreg_paths.items():
            df_session = (
                pd.read_csv(p)
                .assign(mouse_name=mouse_name)[["cell_id", "mouse_name"]]
                .drop_duplicates()
            )
            logreg_files.append(df_session)
        df = pd.concat(logreg_files)
        df["updated_id"] = df.groupby(["cell_id", "mouse_name"]).ngroup()

        for mouse_name, p in logreg_paths.items():
            original = pd.read_csv(p)
            if "updated_id" in original.columns:
                original.drop("updated_id", axis=1, inplace=True)
            updated = df.loc[lambda x: x.mouse_name == mouse_name]
            merged = pd.merge(original, updated)
            merged.to_csv(p, index=False)

    @staticmethod
    def update_data_files(
        logreg_paths: Dict[str, Path], data_paths: Dict[str, List[Path]]
    ):
        for mouse in logreg_paths.keys():
            logreg_file = logreg_paths[mouse]
            data_files = data_paths[mouse]
            df_logreg = pd.read_csv(logreg_file)

            for f in data_files:
                df_data = pd.read_csv(f).drop_duplicates()
                df_data = df_data.merge(
                    df_logreg[["cell_id", "updated_id"]].drop_duplicates()
                )
                df_data.drop("cell_id", axis=1, inplace=True)
                df_data.rename(columns={"updated_id": "cell_id"}, inplace=True)
                df_data.to_csv(f, index=False)

            df_logreg.drop("cell_id", axis=1, inplace=True)
            df_logreg.rename(columns={"updated_id": "cell_id"}, inplace=True)
            df_logreg.to_csv(logreg_paths[mouse])


def main():
    from pprint import pprint

    root_dir = Path(r"E:\Context\PFC - Cohort 1\1p Export")
    cohort = Cohort.PFC
    mouse_dirs = MouseDirFinder(root_dir, cohort).find()
    files: Dict[str, List[Path]] = {}
    for mouse_dir in mouse_dirs:
        files[mouse_dir.name] = FileFinder(mouse_dir, cohort).find()

    logreg_files: Dict[str, Path] = {}
    data_files: Dict[str, List[Path]] = {}
    for mouse, d in files.items():
        print(mouse)
        mouse_data_files = []
        mouse_data_files.extend(d["spikes_files"])
        mouse_data_files.extend(d["trace_files"])
        data_files[mouse] = mouse_data_files
        logreg_files[mouse] = d["logreg_files"][0]

    pprint(data_files)
    updater = IDUpdater()
    updater.update_logreg(logreg_files)
    updater.update_data_files(logreg_files, data_files)


if __name__ == "__main__":
    main()
