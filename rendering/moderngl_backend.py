from __future__ import annotations

import time


class ModernGLBackend:
    """
    Functional fallback renderer.

    Uses GLFW + ModernGL to open a window and draw a PS1-style quantized triangle,
    so the user sees actual output instead of a blank surface.
    """

    name = "moderngl"

    def __init__(self, width: int, height: int, title: str, auto_close_after_frames: int = 0) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.auto_close_after_frames = max(0, auto_close_after_frames)

        self.window = None
        self.ctx = None
        self.program = None
        self.vbo = None
        self.vao = None
        self._closed = False
        self._frame_count = 0
        self._start_time = 0.0

    def initialize(self) -> None:
        import glfw  # type: ignore
        import moderngl  # type: ignore

        if not glfw.init():
            raise RuntimeError("GLFW init failed for ModernGL backend")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if self.window is None:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window for ModernGL backend")

        glfw.make_context_current(self.window)
        self.ctx = moderngl.create_context()
        self.program = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_pos;
                in vec3 in_color;
                out vec3 v_color;
                uniform float u_time;
                void main() {
                    vec2 jitter = vec2(sin(u_time + in_pos.y * 8.0), cos(u_time + in_pos.x * 7.0)) * 0.01;
                    gl_Position = vec4(in_pos + jitter, 0.0, 1.0);
                    v_color = in_color;
                }
            """,
            fragment_shader="""
                #version 330
                in vec3 v_color;
                out vec4 fragColor;
                void main() {
                    vec3 q = floor(v_color * 31.0) / 31.0; // 5-bit style color
                    fragColor = vec4(q, 1.0);
                }
            """,
        )

        vertices = self.ctx.buffer(
            data=(
                -0.6,
                -0.5,
                1.0,
                0.1,
                0.1,
                0.6,
                -0.5,
                0.1,
                1.0,
                0.1,
                0.0,
                0.6,
                0.1,
                0.1,
                1.0,
            )
        )
        self.vbo = vertices
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, "2f 3f", "in_pos", "in_color")])
        self._closed = False
        self._frame_count = 0
        self._start_time = time.perf_counter()

    def begin_frame(self) -> None:
        if self.ctx is None:
            return
        self.ctx.clear(0.08, 0.08, 0.12, 1.0)

    def end_frame(self) -> None:
        import glfw  # type: ignore

        if self.window is None or self.ctx is None or self.vao is None or self.program is None:
            return

        t = time.perf_counter() - self._start_time
        self.program["u_time"].value = t
        self.vao.render()
        glfw.swap_buffers(self.window)
        glfw.poll_events()

        self._frame_count += 1
        if self.auto_close_after_frames > 0 and self._frame_count >= self.auto_close_after_frames:
            self._closed = True

    def should_close(self) -> bool:
        import glfw  # type: ignore

        if self.window is None:
            return True
        return self._closed or bool(glfw.window_should_close(self.window))

    def shutdown(self) -> None:
        import glfw  # type: ignore

        self._closed = True
        if self.vao is not None:
            self.vao.release()
        if self.vbo is not None:
            self.vbo.release()
        if self.program is not None:
            self.program.release()
        if self.window is not None:
            glfw.destroy_window(self.window)
        glfw.terminate()
