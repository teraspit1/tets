from __future__ import annotations

from ecs.scene import Scene


class SceneHierarchyPanel:
    def draw(self, scene: Scene) -> list[str]:
        return [f"{entity}: {node.name}" for entity, node in scene.nodes.items()]


class InspectorPanel:
    def draw(self, selected_entity: int | None, world) -> dict[str, object]:
        if selected_entity is None:
            return {}
        return {
            ctype.__name__: component
            for ctype, bucket in world.components.items()
            if (component := bucket.get(selected_entity)) is not None
        }


class AssetBrowserPanel:
    def draw(self, resource_manager) -> dict[str, list[str]]:
        return {
            "meshes": list(resource_manager.meshes.keys()),
            "textures": list(resource_manager.textures.keys()),
            "shaders": list(resource_manager.shaders.keys()),
        }
