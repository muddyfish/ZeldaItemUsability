from ctypes import *
import mmap
import json

class FileStruct(BigEndianStructure):
    _fields_ = [('vmap_start', c_uint32),
                ('vmap_end', c_uint32),
                ('pmap_start', c_uint32),
                ('pmap_end', c_uint32),]

    def __repr__(self):
        return "FileStruct(%x, %x)"%(self.vmap_start, self.vmap_end)


class FileTableHeader:
    size = 0x30

    def __init__(self, header: memoryview):
        length = 4
        sections = []
        cur_offset = 0
        for i in range(0, FileTableHeader.size, length):
            for j in range(i, i+length):
                if header[j] == 0:
                    if j != i:
                        sections.append(header[cur_offset:j])
                    cur_offset = i+length
                    break
        assert len(sections) == 2
        self.creator, self.build_date = sections

    def __str__(self):
        return "\n".join([bytes(self.creator).decode(),
                          bytes(self.build_date).decode()])


class FileTable:
    def __init__(self, rom_file: memoryview, filetable_offset: int):
        self.load_config()
        self.header = FileTableHeader(rom_file[:FileTableHeader.size])
        print(self.header)
        self.files = []
        end_offset = 0
        cur_offset = FileTableHeader.size
        while cur_offset != end_offset:
            self.files.append(FileStruct.from_buffer(rom_file, cur_offset))
            if self.files[-1].vmap_start == filetable_offset + FileTableHeader.size:
                end_offset = self.files[-1].vmap_end  - filetable_offset
            cur_offset += sizeof(FileStruct)
            assert self.files[-1].pmap_end == 0, "Compressed ROMS aren't supported."

    def load_config(self, filename="config.json"):
        with open(filename) as json_file:
            self.config = json.load(self.config)

    def get_file(self, file_id, rom_file):
        file_struct = self.files[file_id]
        start, end = file_struct.vmap_start, file_struct.vmap_end
        #print(file_id, hex(start), hex(end))
        return memoryview(rom_file)[start:end]


class RomLoader:
    def __init__(self, rom_file: mmap.mmap):
        self.filetable_offset = rom_file.find(b"zelda@")
        memview = memoryview(rom_file)
        self.filetable = FileTable(memview[self.filetable_offset:], self.filetable_offset)