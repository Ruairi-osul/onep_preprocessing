from onep.loadlib import get_mice, load_traces, load_events, get_ofl_exp_phase
from pathlib import Path
import isx


DATA_DIR = Path(r"D:\OFL\processed 1p data")


def main():
    mice = get_mice(DATA_DIR)
    traces = load_traces(mice, ["day2"])
    df = get_ofl_exp_phase(traces, "day2")
    print(df)


if __name__ == "__main__":
    main()
