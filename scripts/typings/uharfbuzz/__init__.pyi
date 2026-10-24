from collections.abc import Mapping

__version__: str

class Face:
    def __init__(self, data: bytes) -> None: ...

class Font:
    def __init__(self, face: Face) -> None: ...

class GlyphInfo:
    codepoint: int
    cluster: int

class GlyphPosition:
    x_advance: int
    y_advance: int
    x_offset: int
    y_offset: int

class Buffer:
    def __init__(self) -> None: ...
    def add_str(self, text: str) -> None: ...
    def guess_segment_properties(self) -> None: ...
    @property
    def glyph_infos(self) -> list[GlyphInfo]: ...
    @property
    def glyph_positions(self) -> list[GlyphPosition]: ...

def shape(font: Font, buffer: Buffer, features: Mapping[str, int]) -> None: ...
