from dataclasses import dataclass
from typing import Tuple
from .tile import Tile

@dataclass(frozen=True)
class Factory:
    tiles: Tuple[Tile, ...]
    
    def is_empty(self) -> bool:
        return len(self.tiles) == 0
        
    def take(self, idx: int) -> Tuple['Factory', Tuple[Tile, ...]]:
        selected_tile = self.tiles[idx]
        matching_tiles = tuple(t for t in self.tiles if t == selected_tile)
        remaining_tiles = tuple(t for t in self.tiles if t != selected_tile)
        return Factory(remaining_tiles), matching_tiles

