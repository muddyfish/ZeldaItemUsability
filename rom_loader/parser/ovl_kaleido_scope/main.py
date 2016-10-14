class OvlKaleidoScopeParser:
    file_id = 33
    filename = "ovl_kaleido_scope"

    def __init__(self, file: memoryview, item_usability_offset: int):
        print(hex(len(file)))