from typing import List

from PIL import Image


class ItemIconStatic:
    filename = "icon_item_static"

    def __init__(self, file: memoryview,
                 no_icons: int,
                 no_items: int,
                 image_size: int,
                 width: int,
                 height: int,
                 del_images: List[int],
                 no_equipment: int,
                 equipment_offset: int):
        self.file = file[:no_icons*image_size]
        self.width = width
        self.height = height
        self.item_images = []
        self.equipment_images = []
        self.images = []
        for i in range(no_items):
            if i in del_images: continue
            self.item_images.append(self.read_rgba32(bytes(self.file[i*image_size:(i+1)*image_size]), width, height))
        for i in range(no_equipment):
            i += equipment_offset
            self.equipment_images.append(self.read_rgba32(bytes(self.file[i*image_size:(i+1)*image_size]), width, height))
        self.images.extend(self.item_images)
        self.images.extend(self.equipment_images)

    def read_rgba32(self, offset, w, h):
        return Image.frombytes('RGBA', (w, h), offset)
