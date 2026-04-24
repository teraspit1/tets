from __future__ import annotations


class ModernGLBackend:
    """
    Fallback backend used only if Vulkan init/import fails.
    This keeps development unblocked while preserving renderer interfaces.
    """

    name = "moderngl"

    def __init__(self, width: int, height: int, title: str) -> None:
        self.width = width
        self.height = height
        self.title = title
        self._closed = False

    def initialize(self) -> None:
        # Creating a full GL context requires a host windowing integration,
        # which is omitted in MVP scaffold; this backend is a no-op placeholder
        # with the same lifecycle hooks.
        self._closed = False

    def begin_frame(self) -> None:
        pass

    def end_frame(self) -> None:
        pass

    def should_close(self) -> bool:
        return self._closed

    def shutdown(self) -> None:
        self._closed = True
