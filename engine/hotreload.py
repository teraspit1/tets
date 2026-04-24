from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class WatchedFile:
    path: Path
    callback: Callable[[Path], None]
    mtime: float = field(default=0.0)


class HotReloadService:
    def __init__(self) -> None:
        self._watches: list[WatchedFile] = []

    def watch(self, path: str, callback: Callable[[Path], None]) -> None:
        file_path = Path(path)
        mtime = file_path.stat().st_mtime if file_path.exists() else 0.0
        self._watches.append(WatchedFile(path=file_path, callback=callback, mtime=mtime))

    def poll(self) -> None:
        for watch in self._watches:
            if not watch.path.exists():
                continue
            current_mtime = watch.path.stat().st_mtime
            if current_mtime > watch.mtime:
                watch.mtime = current_mtime
                watch.callback(watch.path)
