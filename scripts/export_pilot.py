from typing import List
from pathmodels.base import session_dirs
from pathmodels.find import find_pilot_mouse_dirs
from pathlib import Path
import pandas as pd

p = Path(r"D:\Context\Pilot\data")
out_dir = Path(r"E:\Context\pilot")


def main():
    dirs = find_pilot_mouse_dirs(p)

    out: List[pd.DataFrame] = []
    for d in dirs:
        for session_name, session_dir in d.session_dirs.items():
            f = session_dir.data_dirs["cylander_behaviour"].dlc_trajectory_file
            if f is not None:
                out.append(
                    pd.read_hdf(f).assign(mouse=d.mouse.name, session=session_name)
                )
    df = pd.concat(out)
    for session in df.session.unique():
        df.loc[lambda x: x.session == session].to_parquet(
            out_dir / f"{session}-freeze_motion.parquet.gzip", compression="gzip"
        )


if __name__ == "__main__":
    main()
