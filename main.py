from rom_loader.loader import RomLoader
from rom_loader.parser.ovl_kaleido_scope.main import OvlKaleidoScopeParser
from rom_loader.parser.icon_item_static.main import ItemIconStatic

import mmap

from tkinter import *
import tkinter.filedialog as filedialog

from PIL import ImageTk


class Main:
    def __init__(self):
        self.root = Tk()
        self.create_widgets()
        #self.load_rom()
        #self.finalise_load()
        self.root.mainloop()

    def create_widgets(self):
        self.root.title("ItemUsability Editor")
        self.root_frame = Frame(self.root, height=384, width=455)
        self.root_frame.pack()

        self.canvas = Canvas(self.root_frame, height=384, width=300)
        self.canvas.pack(side=LEFT)

        self.clicked_frame = Frame(self.root_frame, height=192, width=155)
        self.clicked_frame.pack(side=RIGHT)

        self.clicked_canvas = Canvas(self.clicked_frame, height=64, width=64)
        self.clicked_canvas.pack()
        self.clicked_adult = BooleanVar()
        self.clicked_check_adult = Checkbutton(self.clicked_frame, text="Adult", var=self.clicked_adult, command=self.update_clicked)
        self.clicked_check_adult.pack()
        self.clicked_child = BooleanVar()
        self.clicked_check_child = Checkbutton(self.clicked_frame, text="Child", var=self.clicked_child, command=self.update_clicked)
        self.clicked_check_child.pack()

        self.root_menu = Menu(self.root)
        self.menu_file = Menu(self.root_menu, tearoff=0)
        self.menu_file.add_command(label="Open ROM", command=self.select_rom)
        self.menu_file.add_command(label="Save", command=self.save, state="disabled")
        self.menu_file.add_command(label="Exit", command=self.root.quit)

        self.root_menu.add_cascade(label="File", menu=self.menu_file)
        self.root.config(menu=self.root_menu)

    def select_rom(self):
        # Load filesystem
        self.zelootma_filename = filedialog.askopenfilename()
        if self.zelootma_filename:
            self.load_rom(self.zelootma_filename)
            self.finalise_load()

    def finalise_load(self):
        self.menu_file.entryconfig("Save", state="normal")
        self.images = []
        self.tk_images = []
        for i, im in enumerate(self.icon_parser.item_images):
            self.tk_images.append(ImageTk.PhotoImage(master=self.canvas, image=im))
            self.images.append(self.canvas.create_image((i % 6) * (self.icon_parser.width + 16) + 24,
                                                         (i // 6) * (self.icon_parser.height + 16) + 24,
                                                         image=self.tk_images[-1]))
            self.canvas.tag_bind(self.images[-1], '<ButtonPress-1>', self.icon_pressed)

        for i, im in enumerate(self.icon_parser.equipment_images):
            self.tk_images.append(ImageTk.PhotoImage(master=self.canvas, image=im))
            self.images.append(self.canvas.create_image((i % 3) * (self.icon_parser.width + 16) + 24,
                                                         (i // 3) * (self.icon_parser.height + 16) + 216,
                                                         image=self.tk_images[-1]))
            self.canvas.tag_bind(self.images[-1], '<ButtonPress-1>', self.icon_pressed)

        self.clicked = 0
        self.clicked_image = ImageTk.PhotoImage(master=self.canvas, image=self.icon_parser.item_images[0])
        self.clicked_canvas.create_image(24, 24, image=self.clicked_image)
        self.update_checkbuttons()

    def load_rom(self, filename="ZELOOTMA.z64"):
        rom_file = open(filename, "rb+")
        self.rom_mmap = mmap.mmap(rom_file.fileno(), 0, access=mmap.ACCESS_WRITE)
        self.rom_mmap.seek(0)
        self.loader = RomLoader(self.rom_mmap)
        self.pause_menu_parser = self.load_parser(OvlKaleidoScopeParser, self.loader, self.rom_mmap)
        self.icon_parser = self.load_parser(ItemIconStatic, self.loader, self.rom_mmap)
        rom_file.close()

    def save(self):
        self.rom_mmap.flush()

    def load_parser(self, parser, loader, rom_mmap):
        file = loader.filetable.get_file(parser.file_id, rom_mmap)
        config = loader.config[parser.filename].get(loader.version, {})
        config.update(loader.config[parser.filename].get("all", {}))
        for k, v in config.items():
            if k.endswith("_offset") or (isinstance(v, str) and v.startswith("0x")):
                config[k] = int(v, 0)
        return parser(file, **config)

    def icon_pressed(self, event):
        self.clicked = event.widget.find_closest(event.x, event.y)[0] - 1
        self.clicked_image = ImageTk.PhotoImage(master=self.canvas, image=self.icon_parser.images[self.clicked])
        self.clicked_canvas.create_image(24, 24, image=self.clicked_image)
        if str(self.clicked) in self.pause_menu_parser.item_map:
            self.clicked = self.pause_menu_parser.item_map[str(self.clicked)]
        self.update_checkbuttons()

    def update_checkbuttons(self):
        struct = self.pause_menu_parser[self.clicked]
        adult, child = {0: (True, False),
                        1: (False, True),
                        9: (True, True)}[struct]
        self.clicked_adult.set(adult)
        self.clicked_child.set(child)
        self.update_clicked()

    def update_clicked(self):
        adult, child = self.clicked_adult.get(), self.clicked_child.get()
        self.clicked_check_adult.config(state="normal")
        self.clicked_check_child.config(state="normal")
        if adult ^ child:
            if adult:
                self.clicked_check_adult.config(state="disabled")
            if child:
                self.clicked_check_child.config(state="disabled")
        struct = {(1,0): 0,
                  (0,1): 1,
                  (1,1): 9}[adult, child]
        self.pause_menu_parser[self.clicked] = struct


def main():
    main = Main()

if __name__ == "__main__":
    main()