from dataclasses import dataclass
from typing import Tuple
from .tile import Tile
from .factory import Factory
from .table_center import TableCenter
from .bag import BagState, BagOperations
from .used_tiles import UsedTilesState, UsedTilesOperations
from .random_generator import RandomGenerator

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
        if len(state.bag.tiles) < len(state.factories) * 4:
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
