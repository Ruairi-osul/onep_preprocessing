"""
Preprocess all videos for OFL
"""
from onep_preprocessing.get_vids import find_files
from onep_preprocessing.preprocess import preprocess
from pathlib import Path
from pprint import pprint


def main():
    p = Path(r"D:\data")
    files = find_files(p)
    pprint(files)
    for f in files:
        pprint(str(f))
        preprocess(f)


if __name__ == "__main__":
    main()
