"""
Preprocess all videos for PFC animals
"""

from pathmodels.base.session_dirs import SessionDir
from pathmodels.find import find_pfc_mouse_dirs
from onep_preprocessing.preprocess import preprocess
from pathlib import Path
from pprint import pprint
from pathmodels.base.data_dirs import OnePDir


def get_onep_dir(session_dir: SessionDir) -> OnePDir:
    if "one_photon" not in session_dir.data_dirs:
        raise FileNotFoundError("Could not find onep dir")
    onep_dir = session_dir.data_dirs["one_photon"]
    if not onep_dir:
        raise FileNotFoundError("Could not find onep dir")
    return session_dir.data_dirs["one_photon"]


def get_video(onep_dir: OnePDir) -> Path:
    raw_video_file = onep_dir.raw_video_file
    if raw_video_file is None:
        raise FileNotFoundError("Could not find raw video file")
    return raw_video_file


def output_exists(onep_dir: OnePDir) -> bool:
    return onep_dir.default_exports_dir.joinpath("cnmfe_cellset.isxd").exists()


def is_problem_vid(video_file: Path) -> bool:
    PROBLEM_VIDS = [
        "2021-05-19-18-18-29_video_trig_0.isxd",
        "2021-05-11-17-44-13_video_trig_0.isxd",
    ]
    return video_file.name in PROBLEM_VIDS


def main():
    p = Path(r"D:\Context Data\PFC Last\Raw Data")
    dirs = find_pfc_mouse_dirs(p)
    errors = []
    for mouse in dirs:
        for name, session_dir in mouse.session_dirs.items():
            try:
                onep_dir = get_onep_dir(session_dir)
                raw_video_file = get_video(onep_dir)
            except FileNotFoundError as e:
                errors.append(f"{mouse.mouse.name}, {name}, {str(e)}")
                continue
            if output_exists(onep_dir) or is_problem_vid(raw_video_file):
                continue
            outpath = onep_dir.default_exports_dir
            outpath.mkdir(exist_ok=True)
            print(str(raw_video_file))
            preprocess(raw_video_file, out_dir=outpath)
    pprint(errors)


if __name__ == "__main__":
    main()
