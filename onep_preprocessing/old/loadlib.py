from typing import Tuple, List, Optional, NamedTuple, Callable
from spiketimes.binning import which_bin
import numpy as np
from pathlib import Path
import pandas as pd
from .data_obj import Mouse
from collections import namedtuple


class BlockType(NamedTuple):
    name: str
    length: float


def get_mice(parent_output_dir: Path) -> List[Mouse]:
    return list(map(Mouse.from_dir, parent_output_dir.glob("*")))


def load_traces(mice: List[Mouse], session_names: List[str]) -> pd.DataFrame:
    dsets: List[pd.DataFrame] = []
    for mouse in mice:
        for session_name in session_names:
            if not mouse.sessions:
                continue
            session = next(filter(lambda x: x.name == session_name, mouse.sessions))
            if session:
                dsets.append(
                    pd.read_csv(session.exported_trace_file).assign(
                        mouse=mouse.name, session_name=session.name
                    )
                )
    df = pd.concat(dsets)
    return df


def _align_day1() -> List:
    return []


def _align_day2() -> List[BlockType]:
    baseline = BlockType("Baseline", length=180)
    cs = BlockType("CS", length=28)
    us = BlockType("US", length=2)
    iti = BlockType("ITI", length=30)
    post = BlockType("Post", length=180)
    blocks = [baseline]
    blocks.extend([cs, us, iti] * 30)
    blocks = blocks + [post]
    return blocks


def _align_day3() -> List[BlockType]:
    baseline = BlockType("Baseline", length=180)
    cs = BlockType("CS", length=30)
    iti = BlockType("ITI", length=30)
    post = BlockType("Post", length=180)
    blocks = [baseline]
    blocks.extend([cs, iti] * 5)
    blocks = blocks + [post]
    return blocks


def _align_day4() -> List[BlockType]:
    baseline = BlockType("Baseline", length=180)
    cs = BlockType("CS", length=28)
    us = BlockType("US", length=2)
    iti = BlockType("ITI", length=30)
    post = BlockType("Post", length=180)
    blocks = [baseline]
    blocks.extend([cs, us, iti] * 30)
    blocks = blocks + [post]
    return blocks


def load_events(mice: List[Mouse], session_names: List[str]):
    dsets: List[pd.DataFrame] = []
    for mouse in mice:
        for session_name in session_names:
            if not mouse.sessions:
                continue
            session = next(filter(lambda x: x.name == session_name, mouse.sessions))
            if session:
                dsets.append(
                    pd.read_csv(session.exported_events_file).assign(
                        mouse=mouse.name, session_name=session.name
                    )
                )
    df = pd.concat(dsets)
    return df


def _blocks_getter_fac(session_name: str) -> Callable[[], List[BlockType]]:
    if session_name == "day1":
        return _align_day1
    elif session_name == "day2":
        return _align_day2
    elif session_name == "day3":
        return _align_day3
    elif session_name == "day4":
        return _align_day4
    else:
        raise ValueError("Unknown session name")


def _ofl_trial_rule(session_name: str) -> int:
    if session_name == "day1":
        return 0
    elif session_name == "day2":
        return 3
    elif session_name == "day3":
        return 2
    elif session_name == "day4":
        return 3
    else:
        raise ValueError("Unknown session name")


def get_ofl_exp_phase(
    df: pd.DataFrame,
    session_name: str,
    max_latency: Optional[float] = None,
    time_col: str = "time",
) -> pd.DataFrame:
    """Add experimental phase column to a data df

    Args:
        df (pd.DataFrame): df containing data
        session_name (str): name of the session

    Returns:
        pd.DataFrame: [description]
    """
    blocks = _blocks_getter_fac(session_name)()
    block_lengths = np.array(list(map(lambda x: x.length, blocks)))
    block_starts = np.cumsum(np.insert(block_lengths, 0, 0))
    trial_rule = _ofl_trial_rule(session_name)
    trials = [i // trial_rule for i, _ in enumerate(blocks)]
    idx, values = which_bin(
        df[time_col].values, bin_edges=block_starts, max_latency=max_latency,
    )
    trial_mapper = {block_idx: trial for block_idx, trial in enumerate(trials)}
    df = df.assign(
        block_number=idx,
        block_type=lambda x: x.block_number.apply(lambda y: blocks[int(y)].name),
        block_start=values,
        trial_number=lambda x: x["block_number"].map(trial_mapper),
    )
    return df

