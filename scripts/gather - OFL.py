from enum import auto
from dataclasses import dataclass
from onep_preprocessing.gather import export, Cohort
from pathlib import Path
from tkinter.filedialog import askdirectory
from typing import Dict, List

COHORT = Cohort.PFC
ROOT_PATH = Path(r"D:\Context Data\PFC Last\Raw Data")
OUTPUT_PATH = Path(r"D:\Context Data\PFC Last\Export")
EXCLUDED_SESSIONS: Dict[str, List[str]] = {
    "B51618": ["day5-test2"],
    "B51619": [
        "day1-epm",
        "day2-morning",
        "day3-afternoon",
        "day4-test1",
    ],
    "B51629": ["day2-afternoon"],
    "B58216": ["day3-morning"],
    "B58217": ["day3-morning", "day2-afternoon"],
    "B51631": ["day1-epm"],
    "b78763": ["day2-afternoon"]
    
}


def main() -> None:
    # root_path = Path(askdirectory(title="Input root directory"))
    # output_root_dir = Path(askdirectory(title="Output root directory"))
    root_path = ROOT_PATH
    output_root_dir = OUTPUT_PATH

    mouse_paths: List[Path] = list(root_path.glob("*"))
    for mouse_path in mouse_paths:
        print(mouse_path.name)

        export(
            mouse_path,
            cohort=COHORT,
            output_root_dir=output_root_dir,
            excluded_sessions=EXCLUDED_SESSIONS.get(mouse_path.name),
        )


if __name__ == "__main__":

    main()
