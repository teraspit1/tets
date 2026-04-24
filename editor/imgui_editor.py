from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ecs.components import Transform
from ecs.serialization import SceneSerializer
from scripting.graph import VisualScriptGraph
from scripting.nodes import TransformTranslateNode, UpdateEventNode


@dataclass
class ViewportRect:
    x: float = 0.0
    y: float = 0.0
    w: float = 1.0
    h: float = 1.0


class ImGuiEditor:
    def __init__(self, engine, editor_app) -> None:
        self.engine = engine
        self.editor = editor_app
        self.serializer = SceneSerializer()
        self.viewport = ViewportRect()
        self.message = "Ready"
        self.scene_path = Path("assets/scene_autosave.json")

        self.shader_status = "Shader hot reload: idle"
        self._shader_mtimes: dict[str, float] = {}

    def _pick_entity(self, mouse_x: float, mouse_y: float) -> int | None:
        if self.viewport.w <= 1 or self.viewport.h <= 1:
            return None

        best_entity = None
        best_dist = 12.0
        for entity, (transform,) in self.engine.world.query(Transform):
            sx, sy = self._project_to_viewport(transform.position)
            dist = float(np.hypot(mouse_x - sx, mouse_y - sy))
            if dist < best_dist:
                best_dist = dist
                best_entity = entity
        return best_entity

    def _project_to_viewport(self, pos: np.ndarray) -> tuple[float, float]:
        # lightweight top-down projection for editor picking
        nx = np.clip((pos[0] + 10.0) / 20.0, 0.0, 1.0)
        ny = np.clip((pos[2] + 10.0) / 20.0, 0.0, 1.0)
        sx = self.viewport.x + nx * self.viewport.w
        sy = self.viewport.y + ny * self.viewport.h
        return sx, sy

    def _draw_hierarchy(self, imgui) -> None:
        imgui.begin("Hierarchy")
        for entity, node in self.engine.scene.nodes.items():
            selected = self.editor.state.selected_entity == entity
            clicked, _ = imgui.selectable(f"{entity} | {node.name}", selected)
            if clicked:
                self.editor.state.selected_entity = entity
        imgui.end()

    def _draw_inspector(self, imgui) -> None:
        imgui.begin("Inspector")
        entity = self.editor.state.selected_entity
        if entity is None:
            imgui.text("No entity selected")
            imgui.end()
            return

        imgui.text(f"Entity: {entity}")
        transform = self.engine.world.get_component(entity, Transform)
        if transform is not None:
            changed_x, px = imgui.drag_float("Pos X", float(transform.position[0]), 0.05)
            changed_y, py = imgui.drag_float("Pos Y", float(transform.position[1]), 0.05)
            changed_z, pz = imgui.drag_float("Pos Z", float(transform.position[2]), 0.05)
            if changed_x or changed_y or changed_z:
                transform.position[:] = [px, py, pz]
        imgui.end()

    def _draw_assets(self, imgui) -> None:
        imgui.begin("Asset Browser")
        assets = self.editor.asset_browser.draw(getattr(self.engine, "resources", type("R", (), {"meshes": {}, "textures": {}, "shaders": {}})()))
        for key, values in assets.items():
            imgui.text(f"{key}: {', '.join(values) if values else '(empty)'}")
        imgui.separator()
        imgui.text(self.shader_status)
        imgui.end()

    def _draw_toolbar(self, imgui) -> None:
        imgui.begin("Toolbar")
        if imgui.button("Play/Stop"):
            self.editor.toggle_play()
            self.message = f"Play mode: {self.editor.state.play_mode}"
        imgui.same_line()
        if imgui.button("Save Scene"):
            self.scene_path.parent.mkdir(parents=True, exist_ok=True)
            self.serializer.save(self.engine.scene, str(self.scene_path))
            self.message = f"Saved: {self.scene_path}"
        imgui.same_line()
        if imgui.button("Load Scene"):
            if self.scene_path.exists():
                self.serializer.load_into(self.engine.scene, str(self.scene_path))
                self.message = f"Loaded: {self.scene_path}"
            else:
                self.message = f"No scene file: {self.scene_path}"

        imgui.text(self.message)
        imgui.end()

    def _draw_node_editor(self, imgui) -> None:
        imgui.begin("Visual Scripting")
        entity = self.editor.state.selected_entity
        if entity is None:
            imgui.text("Select entity to bind graph")
            imgui.end()
            return

        graph = self.engine.visual_runtime.graphs.get(entity)
        if graph is None and imgui.button("Create default graph"):
            graph = VisualScriptGraph(f"Graph_{entity}")
            update = UpdateEventNode("update")
            translate = TransformTranslateNode("translate")
            graph.add_node(update)
            graph.add_node(translate)
            graph.add_link("update", "flow", "translate", "entity")
            self.engine.visual_runtime.attach_graph(entity, graph)

        graph = self.engine.visual_runtime.graphs.get(entity)
        if graph is not None:
            imgui.text(f"Graph: {graph.name}")
            for node_desc in self.editor.node_editor.list_nodes(graph):
                imgui.bullet_text(node_desc)
            if imgui.button("Execute graph once"):
                self.engine.visual_runtime.update(1.0 / 60.0)
                self.message = "Graph executed"
        imgui.end()

    def _draw_viewport(self, imgui) -> None:
        imgui.begin("Viewport")
        pos = imgui.get_window_position()
        size = imgui.get_content_region_available()
        self.viewport = ViewportRect(pos.x, pos.y + 20, max(1.0, size.x), max(1.0, size.y - 20))

        draw_list = imgui.get_window_draw_list()
        draw_list.add_rect(
            self.viewport.x,
            self.viewport.y,
            self.viewport.x + self.viewport.w,
            self.viewport.y + self.viewport.h,
            imgui.get_color_u32_rgba(0.2, 0.2, 0.25, 1.0),
            0.0,
            0,
            2.0,
        )

        for entity, (transform,) in self.engine.world.query(Transform):
            sx, sy = self._project_to_viewport(transform.position)
            color = imgui.get_color_u32_rgba(1.0, 0.4, 0.2, 1.0)
            if self.editor.state.selected_entity == entity:
                color = imgui.get_color_u32_rgba(0.2, 1.0, 0.4, 1.0)
            draw_list.add_circle_filled(sx, sy, 6.0, color)

        hovered = imgui.is_window_hovered()
        if hovered and imgui.is_mouse_clicked(0):
            mx, my = imgui.get_mouse_pos()
            picked = self._pick_entity(mx, my)
            if picked is not None:
                self.editor.state.selected_entity = picked
                self.message = f"Picked entity {picked}"
        imgui.end()

    def _watch_shader_files(self) -> None:
        shader_root = Path("assets/shaders")
        if not shader_root.exists():
            return

        changed = []
        for shader_file in shader_root.glob("**/*"):
            if shader_file.suffix not in {".vert", ".frag", ".glsl"}:
                continue
            mtime = shader_file.stat().st_mtime
            old = self._shader_mtimes.get(str(shader_file))
            if old is None:
                self._shader_mtimes[str(shader_file)] = mtime
                continue
            if mtime > old:
                self._shader_mtimes[str(shader_file)] = mtime
                changed.append(shader_file.name)

        if changed:
            self.shader_status = f"Shader hot reloaded: {', '.join(changed)}"
            self.message = self.shader_status

    def draw(self, imgui) -> None:
        self._watch_shader_files()
        self._draw_toolbar(imgui)
        self._draw_hierarchy(imgui)
        self._draw_inspector(imgui)
        self._draw_assets(imgui)
        self._draw_viewport(imgui)
        self._draw_node_editor(imgui)
