from typing import List, Dict, Union


class OvlKaleidoScopeParser:
    filename = "ovl_kaleido_scope"

    def __init__(self, file: memoryview,
                 item_usability_offset: int,
                 item_usability_length: int,
                 slot_names: List[str],
                 item_names: List[Union[str, List[str]]],
                 slot_item_map: Dict[str, int],
                 item_map: Dict[int, int]):
        self.file = file[item_usability_offset:item_usability_offset+item_usability_length]
        self.slot_names = slot_names
        self.item_names = item_names
        self.slot_item_map = slot_item_map
        self.item_map = item_map

    def __getitem__(self, item):
        if isinstance(item, str):
            item = self.slot_names.index(item)
        return self.file[item]

    def __setitem__(self, slot, value):
        if isinstance(slot, str):
            slot = self.slot_names.index(slot)
        self.file[slot] = value
        index = self.slot_item_map.get(str(slot), slot)
        slot_names = self.item_names[index]
        item = 0
        for i in self.item_names[:index]:
            if isinstance(i, str):
                item += 1
            else:
                item += len(i)
        if item >= 56:
            item += 3
        if isinstance(slot_names, str):
            no_slots = 1
        else:
            no_slots = len(slot_names)
        slots = [item+0x28+i for i in range(no_slots)]
        for i in slots:
            self.file[i] = value
