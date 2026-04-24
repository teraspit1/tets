from __future__ import annotations


class InventorySystem:
    def __init__(self) -> None:
        self.items: dict[int, dict[str, int]] = {}

    def add_item(self, entity: int, item_id: str, qty: int = 1) -> None:
        bag = self.items.setdefault(entity, {})
        bag[item_id] = bag.get(item_id, 0) + qty

    def remove_item(self, entity: int, item_id: str, qty: int = 1) -> None:
        bag = self.items.setdefault(entity, {})
        if item_id not in bag:
            return
        bag[item_id] = max(0, bag[item_id] - qty)
        if bag[item_id] == 0:
            del bag[item_id]
