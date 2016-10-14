from rom_loader.loader import RomLoader
from rom_loader.parser.ovl_kaleido_scope.main import OvlKaleidoScopeParser

import mmap
from contextlib import closing


def load_rom(filename = "ZELOOTMA.z64"):
    with open(filename, "rb+") as rom_file:
        with closing(mmap.mmap(rom_file.fileno(), 0, access=mmap.ACCESS_WRITE)) as rom_mmap:
            rom_mmap.seek(0)
            loader = RomLoader(rom_mmap)
            pause_menu_parser = load_parser(OvlKaleidoScopeParser, loader, rom_mmap)

            del loader


def load_parser(parser, loader, rom_mmap):
    file = loader.filetable.get_file(parser.file_id, rom_mmap)
    return parser(file)

def main():
    load_rom()

if __name__ == "__main__":
    main()