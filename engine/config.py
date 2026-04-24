from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class EngineConfig:
    window_title: str = "TETS Engine"
    width: int = 1280
    height: int = 720
    target_fps: int = 60
    backend: str = "vulkan"  # vulkan | moderngl
    low_res_scale: float = 0.5
    vsync: bool = True
    fallback_auto_close_frames: int = 0


class ConfigManager:
    def __init__(self, path: str = "engine_config.json") -> None:
        self.path = Path(path)

    def load(self) -> EngineConfig:
        if not self.path.exists():
            config = EngineConfig()
            self.save(config)
            return config

        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return EngineConfig(**payload)

    def save(self, config: EngineConfig) -> None:
        self.path.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
