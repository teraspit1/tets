from __future__ import annotations


def run_editor(engine, editor_app, max_frames: int | None = None) -> None:
    try:
        from imgui_bundle import hello_imgui, imgui, immapp  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "imgui_bundle is required for editor mode. Install with: pip install imgui-bundle"
        ) from exc

    from editor.imgui_editor import ImGuiEditor

    gui = ImGuiEditor(engine, editor_app)
    engine.initialize()

    frame_count = {"value": 0}

    runner_params = hello_imgui.RunnerParams()
    runner_params.app_window_params.window_title = f"{engine.config.window_title} Editor"
    runner_params.app_window_params.window_geometry.size = (
        int(engine.config.width),
        int(engine.config.height),
    )

    def show_gui() -> None:
        engine.tick()
        gui.draw(imgui)
        frame_count["value"] += 1
        if max_frames is not None and frame_count["value"] >= max_frames:
            runner_params.app_shall_exit = True

    def before_exit() -> None:
        engine.shutdown()

    runner_params.callbacks.show_gui = show_gui
    runner_params.callbacks.before_exit = before_exit

    immapp.run(runner_params)
