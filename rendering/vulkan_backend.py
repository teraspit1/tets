from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SwapchainInfo:
    width: int
    height: int
    image_count: int = 2


class VulkanBackend:
    """
    Vulkan bootstrap scaffold.

    NOTE: This class currently opens a Vulkan-compatible GLFW window and handles
    app lifecycle only. It does not yet record command buffers or present drawn
    images, so it should not be used as the active render path for visible output.
    """

    name = "vulkan"
    supports_visible_rendering = False

    def __init__(self, width: int, height: int, title: str) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.swapchain = SwapchainInfo(width, height)
        self.available = False

    def initialize(self) -> None:
        import glfw  # type: ignore

        glfw.init()
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        self.available = self.window is not None

    def begin_frame(self) -> None:
        pass

    def end_frame(self) -> None:
        import glfw  # type: ignore

        glfw.poll_events()

    def should_close(self) -> bool:
        import glfw  # type: ignore

        return bool(self.window is None or glfw.window_should_close(self.window))

    def shutdown(self) -> None:
        import glfw  # type: ignore

        if self.window is not None:
            glfw.destroy_window(self.window)
        glfw.terminate()
