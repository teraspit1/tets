from __future__ import annotations

from engine.config import EngineConfig
from rendering.pipeline import Pipeline, PS1PipelineConfig


class Renderer:
    def __init__(self, config: EngineConfig) -> None:
        self.config = config
        self.pipeline = Pipeline(
            PS1PipelineConfig(
                low_res_scale=config.low_res_scale,
                affine_texture_warp=True,
                vertex_jitter=0.02,
                dithering=True,
            )
        )
        self.backend = None
        self.backend_name = "unknown"

    def initialize(self) -> None:
        if self.config.backend == "vulkan":
            try:
                from rendering.vulkan_backend import VulkanBackend

                self.backend = VulkanBackend(self.config.width, self.config.height, self.config.window_title)
                self.backend.initialize()
                self.backend_name = self.backend.name
                return
            except Exception:
                pass

        from rendering.moderngl_backend import ModernGLBackend

        self.backend = ModernGLBackend(self.config.width, self.config.height, self.config.window_title)
        self.backend.initialize()
        self.backend_name = self.backend.name

    def render(self, scene, debug_overlay) -> None:
        if self.backend is None:
            return
        self.backend.begin_frame()
        _ = scene
        _ = debug_overlay.as_text()
        self.backend.end_frame()

    def should_close(self) -> bool:
        return True if self.backend is None else self.backend.should_close()

    def shutdown(self) -> None:
        if self.backend:
            self.backend.shutdown()
