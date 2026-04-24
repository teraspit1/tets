from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, is_dataclass
from typing import Any, Type


class ECSWorld:
    def __init__(self) -> None:
        self._next_entity_id = 1
        self.entities: set[int] = set()
        self.components: dict[type, dict[int, Any]] = defaultdict(dict)

    def create_entity(self) -> int:
        entity = self._next_entity_id
        self._next_entity_id += 1
        self.entities.add(entity)
        return entity

    def destroy_entity(self, entity: int) -> None:
        self.entities.discard(entity)
        for bucket in self.components.values():
            bucket.pop(entity, None)

    def add_component(self, entity: int, component: Any) -> None:
        self.components[type(component)][entity] = component

    def get_component(self, entity: int, component_type: Type[Any]) -> Any | None:
        return self.components[component_type].get(entity)

    def query(self, *component_types: Type[Any]) -> list[tuple[int, list[Any]]]:
        if not component_types:
            return []
        candidates = self.entities.copy()
        for ctype in component_types:
            candidates &= set(self.components[ctype].keys())
        result = []
        for entity in sorted(candidates):
            result.append((entity, [self.components[ctype][entity] for ctype in component_types]))
        return result

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"entities": sorted(self.entities), "components": {}}
        for ctype, entries in self.components.items():
            payload["components"][ctype.__name__] = {
                str(entity): asdict(component) if is_dataclass(component) else vars(component)
                for entity, component in entries.items()
            }
        return payload
