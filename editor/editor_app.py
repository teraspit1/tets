from __future__ import annotations

from dataclasses import dataclass

from editor.node_editor import NodeEditor
from editor.panels import AssetBrowserPanel, InspectorPanel, SceneHierarchyPanel


@dataclass
class EditorState:
    selected_entity: int | None = None
    play_mode: bool = False


class EditorApp:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.state = EditorState()
        self.scene_hierarchy = SceneHierarchyPanel()
        self.inspector = InspectorPanel()
        self.asset_browser = AssetBrowserPanel()
        self.node_editor = NodeEditor()

    def toggle_play(self) -> None:
        self.state.play_mode = not self.state.play_mode

    def draw(self) -> dict[str, object]:
        """
        Editor draw data model. Hook pyimgui rendering here in production:
        - Scene hierarchy panel
        - Inspector panel
        - Viewport panel
        - Asset browser
        - Visual scripting graph panel
        """
        scene_lines = self.scene_hierarchy.draw(self.engine.scene)
        inspect = self.inspector.draw(self.state.selected_entity, self.engine.world)
        assets = self.asset_browser.draw(getattr(self.engine, "resources", type("R", (), {"meshes": {}, "textures": {}, "shaders": {}})()))
        return {
            "play_mode": self.state.play_mode,
            "scene": scene_lines,
            "inspector": inspect,
            "assets": assets,
            "viewport": "Live viewport bound to renderer output",
        }
