from dataclasses import dataclass
from typing import Tuple
from .tile import Tile

@dataclass(frozen=True)
class UsedTilesState:
    tiles: Tuple[Tile, ...]

class UsedTilesOperations:
    @staticmethod
    def give(state: UsedTilesState, new_tiles: Tuple[Tile, ...]) -> UsedTilesState:
        return UsedTilesState(state.tiles + new_tiles)
    
    @staticmethod
    def take_all(state: UsedTilesState) -> Tuple[UsedTilesState, Tuple[Tile, ...]]:
        return UsedTilesState(tuple()), state.tiles
    
    @staticmethod
    def get_state(state: UsedTilesState) -> str:
        return f"UsedTiles({','.join(str(t) for t in state.tiles)})"

