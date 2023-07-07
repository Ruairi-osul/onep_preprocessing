from pathlib import Path
from typing import Union


class DirectoryCopier:
    def __init__(self, depth: int = 2):
        self.depth = depth

    def copy_directories(
        self,
        source: Union[str, Path],
        target: Union[str, Path],
        _current_depth: int = 0,
    ) -> None:
        # Check if the depth limit has been reached
        if _current_depth > self.depth:
            return

        # Convert strings to Path objects if necessary
        source = Path(source) if isinstance(source, str) else source
        target = Path(target) if isinstance(target, str) else target

        target.mkdir(parents=True, exist_ok=True)

        for item in source.iterdir():
            if item.is_dir():
                new_target = target / item.name
                new_target.mkdir(exist_ok=True)

                # Recursive call to copy subdirectories
                self.copy_directories(item, new_target, _current_depth + 1)
