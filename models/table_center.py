from dataclasses import dataclass
from typing import Tuple
from .tile import Tile

@dataclass(frozen=True)
class TableCenter:
    tiles: Tuple[Tile, ...]
    
    def add(self, new_tiles: Tuple[Tile, ...]) -> 'TableCenter':
        return TableCenter(self.tiles + new_tiles)
        
    def take(self, idx: int) -> Tuple['TableCenter', Tuple[Tile, ...]]:
        selected_tile = self.tiles[idx]
        matching_tiles = tuple(t for t in self.tiles if t == selected_tile)
        remaining_tiles = tuple(t for t in self.tiles if t != selected_tile)
        return TableCenter(remaining_tiles), matching_tiles

