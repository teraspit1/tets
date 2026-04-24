from __future__ import annotations


def run_editor(engine, editor_app, max_frames: int | None = None) -> None:
    import glfw  # type: ignore
    import imgui  # type: ignore
    from imgui.integrations.glfw import GlfwRenderer  # type: ignore

    from editor.imgui_editor import ImGuiEditor

    if not glfw.init():
        raise RuntimeError("GLFW init failed for editor")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    window = glfw.create_window(engine.config.width, engine.config.height, f"{engine.config.window_title} Editor", None, None)
    if window is None:
        glfw.terminate()
        raise RuntimeError("Failed to create editor window")

    glfw.make_context_current(window)
    imgui.create_context()
    impl = GlfwRenderer(window)

    gui = ImGuiEditor(engine, editor_app)

    engine.initialize()
    frame = 0
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        engine.tick()
        gui.draw(imgui)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

        frame += 1
        if max_frames is not None and frame >= max_frames:
            break

    impl.shutdown()
    glfw.destroy_window(window)
    glfw.terminate()
    engine.shutdown()
