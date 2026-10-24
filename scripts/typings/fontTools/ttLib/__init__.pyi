from collections.abc import Mapping
from pathlib import Path
from types import TracebackType
from typing import Protocol, Self

from fontTools.pens.basePen import BasePen

class Glyph(Protocol):
    width: float
    def draw(self, pen: BasePen) -> None: ...

class Head(Protocol):
    unitsPerEm: int

class TTFont:
    def __init__(self, path: Path) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
    def getGlyphSet(self) -> Mapping[str, Glyph]: ...
    def getBestCmap(self) -> dict[int, str] | None: ...
    def getGlyphName(self, glyph_id: int) -> str: ...
    def __getitem__(self, key: str) -> Head: ...
