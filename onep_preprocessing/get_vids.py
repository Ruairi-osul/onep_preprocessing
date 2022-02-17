from pathlib import Path
from typing import List, Dict, Pattern
import re
from pprint import pprint


def find_files(parent_dir: Path) -> List[Path]:
    def _find_mouse_dirs(main_dir: Path) -> List[Path]:
        return [p for p in main_dir.glob("*") if p.is_dir()]

    def _find_session_dirs(mouse_dir: Path) -> Dict[str, Path]:
        expected_sessions: Dict[str, Pattern[str]] = {
            "day1": re.compile(r"day1"),
            "day2": re.compile(r"day2"),
            "day3": re.compile(r"day3"),
            "day4": re.compile(r"day4"),
        }
        out: Dict[str, Path] = {}
        pat = re.compile(r"day\d")
        all_dirs = [p for p in mouse_dir.glob("*") if p.is_dir() and pat.search(p.name)]
        for session_name, pattern in expected_sessions.items():
            out[session_name] = next(x for x in all_dirs if pattern.search(x.name))
        return out

    def _find_all_isx(p: Path) -> List[Path]:
        all_isx: List[Path] = [f for f in p.rglob("*.isxd")]
        return all_isx

    def _check_multiple_isx_files(isx_files: List[Path]) -> bool:
        return len(isx_files) > 1

    def _print_excluded(excluded: Dict[str, List[str]]) -> None:
        print("EXCLUDED: ")
        pprint(excluded)

    excluded: Dict[str, List[str]] = {}
    isx_files: List[Path] = []
    mouse_dirs = _find_mouse_dirs(parent_dir)
    for mouse_dir in mouse_dirs:
        session_dirs = _find_session_dirs(mouse_dir)
        for session_name, session_dir in session_dirs.items():
            all_isx = _find_all_isx(session_dir)
            has_multiple = _check_multiple_isx_files(all_isx)
            if has_multiple:
                excluded[f"{mouse_dir.name} - {session_name}"] = [
                    str(f) for f in all_isx
                ]
                continue
            for f in all_isx:
                isx_files.append(f)

    _print_excluded(excluded)
    return isx_files


if __name__ == "__main__":
    p = Path(r"D:\data")
    files = find_files(p)
    pprint(files)
