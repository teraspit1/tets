from __future__ import annotations


class ModernGLBackend:
    """
    Fallback backend used only if Vulkan init/import fails.

    This backend does not create a real GL context yet, so it auto-closes after
    a configurable number of frames to prevent hanging in non-graphical envs.
    """

    name = "moderngl"

    def __init__(self, width: int, height: int, title: str, auto_close_after_frames: int = 1) -> None:
        self.width = width
        self.height = height
        self.title = title
        self._closed = False
        self._frame_count = 0
        self.auto_close_after_frames = max(1, auto_close_after_frames)

    def initialize(self) -> None:
        self._closed = False
        self._frame_count = 0

    def begin_frame(self) -> None:
        pass

    def end_frame(self) -> None:
        self._frame_count += 1
        if self._frame_count >= self.auto_close_after_frames:
            self._closed = True

    def should_close(self) -> bool:
        return self._closed

    def shutdown(self) -> None:
        self._closed = True
