from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ecs.components import AABBCollider, Camera, MeshRenderer, RigidBody, Transform
from ecs.serialization import SceneSerializer
from scripting.graph import VisualScriptGraph
from scripting.nodes import AddNode, BranchNode, StartEventNode, TransformTranslateNode, UpdateEventNode


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
        self.new_entity_name = "GameObject"

        self.shader_status = "Shader hot reload: idle"
        self._shader_mtimes: dict[str, float] = {}

        self.mesh_name = "mesh"
        self.mesh_path = "meshes/model.obj"
        self.texture_name = "albedo"
        self.texture_path = "textures/albedo.png"
        self.shader_name = "basic"
        self.shader_vert = "shaders/basic.vert"
        self.shader_frag = "shaders/basic.frag"

        self.link_src = ""
        self.link_src_pin = "flow"
        self.link_dst = ""
        self.link_dst_pin = "entity"

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
        nx = np.clip((pos[0] + 10.0) / 20.0, 0.0, 1.0)
        ny = np.clip((pos[2] + 10.0) / 20.0, 0.0, 1.0)
        sx = self.viewport.x + nx * self.viewport.w
        sy = self.viewport.y + ny * self.viewport.h
        return sx, sy

    def _input_text(self, imgui, label: str, value: str) -> str:
        ret = imgui.input_text(label, value)
        if isinstance(ret, tuple):
            return ret[1]
        return value

    def _imgui_window_pos(self, imgui):
        fn = getattr(imgui, "get_window_pos", None) or getattr(imgui, "get_window_position", None)
        return fn() if fn is not None else type("P", (), {"x": 0.0, "y": 0.0})()

    def _imgui_content_region_avail(self, imgui):
        fn = getattr(imgui, "get_content_region_avail", None) or getattr(imgui, "get_content_region_available", None)
        return fn() if fn is not None else type("S", (), {"x": 1.0, "y": 1.0})()

    def _imgui_mouse_pos(self, imgui):
        fn = getattr(imgui, "get_mouse_pos", None)
        return fn() if fn is not None else type("M", (), {"x": 0.0, "y": 0.0})()

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

        imgui.separator()
        self.new_entity_name = self._input_text(imgui, "Entity Name", self.new_entity_name)
        if imgui.button("Create Entity"):
            entity = self.engine.scene.create_node(self.new_entity_name or "GameObject")
            self.engine.world.add_component(entity, Transform())
            self.editor.state.selected_entity = entity
            self.message = f"Created entity {entity}"

        imgui.text(self.message)
        imgui.end()

    def _draw_hierarchy(self, imgui) -> None:
        imgui.begin("Hierarchy")
        for entity, node in list(self.engine.scene.nodes.items()):
            selected = self.editor.state.selected_entity == entity
            selected_ret = imgui.selectable(f"{entity} | {node.name}", selected)
            clicked = selected_ret[0] if isinstance(selected_ret, tuple) else bool(selected_ret)
            if clicked:
                self.editor.state.selected_entity = entity

        if self.editor.state.selected_entity is not None and imgui.button("Delete Selected"):
            target = self.editor.state.selected_entity
            self.engine.scene.remove_node(target)
            self.editor.state.selected_entity = None
            self.message = f"Deleted entity {target}"
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

        imgui.separator()
        if imgui.button("Add Transform") and self.engine.world.get_component(entity, Transform) is None:
            self.engine.world.add_component(entity, Transform())
        imgui.same_line()
        if imgui.button("Add RigidBody") and self.engine.world.get_component(entity, RigidBody) is None:
            self.engine.world.add_component(entity, RigidBody())
        imgui.same_line()
        if imgui.button("Add AABB") and self.engine.world.get_component(entity, AABBCollider) is None:
            self.engine.world.add_component(entity, AABBCollider())

        if imgui.button("Add Camera") and self.engine.world.get_component(entity, Camera) is None:
            self.engine.world.add_component(entity, Camera())
        imgui.same_line()
        if imgui.button("Add MeshRenderer") and self.engine.world.get_component(entity, MeshRenderer) is None:
            self.engine.world.add_component(entity, MeshRenderer(mesh_id="mesh", material_id="mat"))

        imgui.end()

    def _draw_assets(self, imgui) -> None:
        imgui.begin("Asset Browser")
        rm = self.engine.resources

        self.mesh_name = self._input_text(imgui, "Mesh Name", self.mesh_name)
        self.mesh_path = self._input_text(imgui, "Mesh Path", self.mesh_path)
        if imgui.button("Register Mesh"):
            rm.register_mesh(self.mesh_name, self.mesh_path)

        self.texture_name = self._input_text(imgui, "Texture Name", self.texture_name)
        self.texture_path = self._input_text(imgui, "Texture Path", self.texture_path)
        if imgui.button("Register Texture"):
            rm.register_texture(self.texture_name, self.texture_path)

        self.shader_name = self._input_text(imgui, "Shader Name", self.shader_name)
        self.shader_vert = self._input_text(imgui, "Shader Vert", self.shader_vert)
        self.shader_frag = self._input_text(imgui, "Shader Frag", self.shader_frag)
        if imgui.button("Register Shader"):
            rm.register_shader(self.shader_name, self.shader_vert, self.shader_frag)

        imgui.separator()
        imgui.text(f"Meshes: {', '.join(rm.meshes.keys()) or '(none)'}")
        imgui.text(f"Textures: {', '.join(rm.textures.keys()) or '(none)'}")
        imgui.text(f"Shaders: {', '.join(rm.shaders.keys()) or '(none)'}")
        imgui.text(self.shader_status)
        imgui.end()

    def _draw_viewport(self, imgui) -> None:
        imgui.begin("Viewport")
        pos = self._imgui_window_pos(imgui)
        size = self._imgui_content_region_avail(imgui)
        self.viewport = ViewportRect(pos.x, pos.y + 20, max(1.0, float(size.x)), max(1.0, float(size.y - 20)))

        imgui.text("Viewport picking area (click to select nearest entity)")
        if hasattr(imgui, "invisible_button"):
            imgui.invisible_button("viewport_canvas", (self.viewport.w, self.viewport.h))

        hovered = imgui.is_window_hovered() if hasattr(imgui, "is_window_hovered") else False
        if hovered and imgui.is_mouse_clicked(0):
            mouse = self._imgui_mouse_pos(imgui)
            picked = self._pick_entity(float(mouse.x), float(mouse.y))
            if picked is not None:
                self.editor.state.selected_entity = picked
                self.message = f"Picked entity {picked}"
        imgui.end()

    def _draw_node_editor(self, imgui) -> None:
        imgui.begin("Visual Scripting")
        entity = self.editor.state.selected_entity
        if entity is None:
            imgui.text("Select entity to bind graph")
            imgui.end()
            return

        graph = self.engine.visual_runtime.graphs.get(entity)
        if graph is None and imgui.button("Create Graph"):
            graph = VisualScriptGraph(f"Graph_{entity}")
            self.engine.visual_runtime.attach_graph(entity, graph)

        graph = self.engine.visual_runtime.graphs.get(entity)
        if graph is None:
            imgui.end()
            return

        imgui.text(f"Graph: {graph.name}")
        if imgui.button("Add Start"):
            graph.add_node(StartEventNode(f"start_{len(graph.nodes)}"))
        imgui.same_line()
        if imgui.button("Add Update"):
            graph.add_node(UpdateEventNode(f"update_{len(graph.nodes)}"))
        imgui.same_line()
        if imgui.button("Add Branch"):
            graph.add_node(BranchNode(f"branch_{len(graph.nodes)}"))

        if imgui.button("Add AddNode"):
            graph.add_node(AddNode(f"add_{len(graph.nodes)}"))
        imgui.same_line()
        if imgui.button("Add Translate"):
            graph.add_node(TransformTranslateNode(f"translate_{len(graph.nodes)}"))

        self.link_src = self._input_text(imgui, "Src Node", self.link_src)
        self.link_src_pin = self._input_text(imgui, "Src Pin", self.link_src_pin)
        self.link_dst = self._input_text(imgui, "Dst Node", self.link_dst)
        self.link_dst_pin = self._input_text(imgui, "Dst Pin", self.link_dst_pin)
        if imgui.button("Create Link") and self.link_src and self.link_dst:
            if self.link_src in graph.nodes and self.link_dst in graph.nodes:
                graph.add_link(self.link_src, self.link_src_pin, self.link_dst, self.link_dst_pin)
                self.message = "Link created"

        imgui.separator()
        for node_desc in self.editor.node_editor.list_nodes(graph):
            imgui.bullet_text(node_desc)
        imgui.text(f"Links: {len(graph.links)}")
        if imgui.button("Execute graph once"):
            self.engine.visual_runtime.update(1.0 / 60.0)
            self.message = "Graph executed"
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
        if hasattr(imgui, "dock_space_over_viewport"):
            imgui.dock_space_over_viewport()
        self._watch_shader_files()
        self._draw_toolbar(imgui)
        self._draw_hierarchy(imgui)
        self._draw_inspector(imgui)
        self._draw_assets(imgui)
        self._draw_viewport(imgui)
        self._draw_node_editor(imgui)
