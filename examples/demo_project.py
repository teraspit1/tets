from __future__ import annotations

import argparse

from editor.editor_app import EditorApp
from engine.app import EngineApp
from ecs.components import AABBCollider, Camera, MeshRenderer, RigidBody, Transform
from scripting.graph import VisualScriptGraph
from scripting.nodes import TransformTranslateNode, UpdateEventNode
from templates.character_controller import CharacterController
from templates.inventory_system import InventorySystem
from templates.shooting_system import ShootingSystem
from templates.time_system import TimeOfDaySystem
from templates.vehicle_system import VehicleSystem


def build_demo(engine: EngineApp) -> EditorApp:
    camera = engine.scene.create_node("Main Camera")
    engine.world.add_component(camera, Transform())
    engine.world.add_component(camera, Camera(is_main=True))

    player = engine.scene.create_node("Player")
    engine.world.add_component(player, Transform())
    engine.world.add_component(player, MeshRenderer(mesh_id="player_mesh", material_id="player_mat"))
    engine.world.add_component(player, RigidBody())
    engine.world.add_component(player, AABBCollider())

    graph = VisualScriptGraph("PlayerGraph")
    ev = UpdateEventNode("update_0")
    move = TransformTranslateNode("translate_0")
    graph.add_node(ev)
    graph.add_node(move)
    graph.add_link("update_0", "flow", "translate_0", "entity")
    engine.visual_runtime.attach_graph(player, graph)

    engine.character_controller = CharacterController()
    engine.shooting_system = ShootingSystem()
    engine.time_system = TimeOfDaySystem()
    engine.inventory_system = InventorySystem()
    engine.vehicle_system = VehicleSystem()

    return EditorApp(engine)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TETS engine demo project")
    parser.add_argument("--max-frames", type=int, default=None, help="Optional hard cap for update frames")
    parser.add_argument("--mode", choices=["editor", "game"], default="editor", help="Launch mode")
    args = parser.parse_args()

    engine = EngineApp()
    editor = build_demo(engine)
    _ = editor.draw()

    if args.mode == "editor":
        from editor.run_editor import run_editor

        run_editor(engine, editor, max_frames=args.max_frames)
    else:
        engine.run(max_frames=args.max_frames)


if __name__ == "__main__":
    main()
