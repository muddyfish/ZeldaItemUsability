from typing import List, Dict, Union

class OvlKaleidoScopeParser:
    file_id = 33
    filename = "ovl_kaleido_scope"

    def __init__(self, file: memoryview,
                 item_usability_offset: int,
                 item_usability_length: int,
                 slot_names: List[str],
                 item_names: List[Union[str, List[str]]],
                 slot_item_map: Dict[int, int],
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

    def __setitem__(self, item, value):
        if isinstance(item, str):
            item = self.slot_names.index(item)
        self.file[item] = value
        slot_names = self.slot_names[self.slot_item_map.get(item, item)]
        if isinstance(slot_names, str):
            no_slots = 1
        else:
            no_slots = len(slot_names)
        slots = [item+0x28+i for i in range(no_slots)]
        for i in slots:
            self.file[i] = value
