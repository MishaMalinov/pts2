from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
import random
from typing import Protocol

class Tile(Enum):
    STARTING_PLAYER = "S"
    RED = "R"
    BLUE = "B"
    YELLOW = "Y"
    BLACK = "K"
    WHITE = "W"

    def __str__(self):
        return self.value

class RandomGenerator(Protocol):
    def next_int(self, bound: int) -> int:
        pass

class DefaultRandomGenerator:
    def next_int(self, bound: int) -> int:
        return random.randint(0, bound - 1)

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

@dataclass(frozen=True)
class TableAreaState:
    factories: Tuple[Factory, ...]
    table_center: TableCenter
    bag: BagState
    used_tiles: UsedTilesState

class TableAreaOperations:
    @staticmethod
    def take_tiles(
        state: TableAreaState,
        source_idx: int,
        idx: int
    ) -> Tuple[TableAreaState, Tuple[Tile, ...]]:
        if source_idx == len(state.factories):
            new_center, taken_tiles = state.table_center.take(idx)
            return TableAreaState(
                state.factories,
                new_center,
                state.bag,
                state.used_tiles
            ), taken_tiles
        else:
            factory = state.factories[source_idx]
            new_factory, taken_tiles = factory.take(idx)
            new_factories = state.factories[:source_idx] + (new_factory,) + state.factories[source_idx + 1:]
            
            if not new_factory.is_empty():
                new_center = state.table_center.add(new_factory.tiles)
            else:
                new_center = state.table_center
                
            return TableAreaState(
                new_factories,
                new_center,
                state.bag,
                state.used_tiles
            ), taken_tiles
    
    @staticmethod
    def is_round_end(state: TableAreaState) -> bool:
        return all(f.is_empty() for f in state.factories) and len(state.table_center.tiles) == 0
    
    @staticmethod
    def start_new_round(
        state: TableAreaState,
        random_gen: RandomGenerator
    ) -> TableAreaState:
        # Reset factories
        if len(state.bag.tiles) < len(state.factories) * 4:
            # Move tiles from used to bag
            empty_used, used_tiles = UsedTilesOperations.take_all(state.used_tiles)
            new_bag = BagState(state.bag.tiles + used_tiles)
        else:
            empty_used = state.used_tiles
            new_bag = state.bag
            
        new_factories = []
        current_bag = new_bag
        
        for _ in range(len(state.factories)):
            current_bag, tiles = BagOperations.take(current_bag, 4, random_gen)
            new_factories.append(Factory(tiles))
            
        return TableAreaState(
            tuple(new_factories),
            TableCenter(tuple()),
            current_bag,
            empty_used
        )
    
    @staticmethod
    def get_state(state: TableAreaState) -> str:
        parts = []
        for i, factory in enumerate(state.factories):
            parts.append(f"Factory{i}({','.join(str(t) for t in factory.tiles)})")
        parts.append(f"Center({','.join(str(t) for t in state.table_center.tiles)})")
        parts.append(BagOperations.get_state(state.bag))
        parts.append(UsedTilesOperations.get_state(state.used_tiles))
        return "|".join(parts)