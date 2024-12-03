from dataclasses import dataclass
from typing import Tuple
from .tile import Tile
from .random_generator import RandomGenerator

@dataclass(frozen=True)
class BagState:
    tiles: Tuple[Tile, ...]

class BagOperations:
    @staticmethod
    def take(state: BagState, count: int, random_gen: RandomGenerator) -> Tuple[BagState, Tuple[Tile, ...]]:
        if len(state.tiles) < count:
            return state, tuple()
            
        taken_tiles = []
        remaining_tiles = list(state.tiles)
        
        for _ in range(count):
            if not remaining_tiles:
                break
            idx = random_gen.next_int(len(remaining_tiles))
            taken_tiles.append(remaining_tiles.pop(idx))
            
        return BagState(tuple(remaining_tiles)), tuple(taken_tiles)
    
    @staticmethod
    def get_state(state: BagState) -> str:
        return f"Bag({','.join(str(t) for t in state.tiles)})"

