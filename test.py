import unittest
from typing import Tuple, List
from dataclasses import dataclass

# Import your game classes here
from models import (
    Tile, Factory, TableCenter, BagState, UsedTilesState, 
    TableAreaState, TableAreaOperations, BagOperations,
    UsedTilesOperations, RandomGenerator
)

class MockRandomGenerator:
    def __init__(self, sequence: List[int]):
        self.sequence = sequence
        self.current = 0
        
    def next_int(self, bound: int) -> int:
        if self.current >= len(self.sequence):
            return 0  # Default to 0 if we run out of sequence
        value = self.sequence[self.current] % bound  # Ensure the value is within bounds
        self.current += 1
        return value

class AzulGameTest(unittest.TestCase):
    def setUp(self):
        # Create a larger initial tile set for testing
        self.initial_tiles = tuple(
            [tile for tile in [Tile.RED, Tile.BLUE, Tile.YELLOW, Tile.BLACK, Tile.WHITE] for _ in range(4)]
        )
        self.bag_state = BagState(self.initial_tiles)
        self.used_tiles_state = UsedTilesState(tuple())
        
    def test_factory_operations(self):
        # Test factory creation and tile taking
        factory = Factory((Tile.RED, Tile.BLUE, Tile.RED, Tile.YELLOW))
        
        # Test taking all red tiles
        new_factory, taken_tiles = factory.take(0)  # Take RED at index 0
        self.assertEqual(taken_tiles, (Tile.RED, Tile.RED))
        self.assertEqual(new_factory.tiles, (Tile.BLUE, Tile.YELLOW))
        
        # Test empty check
        self.assertFalse(factory.is_empty())
        self.assertFalse(new_factory.is_empty())
        self.assertTrue(Factory(tuple()).is_empty())

    def test_table_center(self):
        center = TableCenter(tuple())
        
        # Test adding tiles
        new_center = center.add((Tile.RED, Tile.BLUE))
        self.assertEqual(new_center.tiles, (Tile.RED, Tile.BLUE))
        
        # Test taking tiles
        final_center, taken = new_center.take(0)  # Take RED at index 0
        self.assertEqual(taken, (Tile.RED,))
        self.assertEqual(final_center.tiles, (Tile.BLUE,))

    def test_bag_operations(self):
        # Test taking tiles with predetermined random sequence
        mock_random = MockRandomGenerator([0, 1])
        
        new_bag, taken = BagOperations.take(self.bag_state, 2, mock_random)
        
        self.assertEqual(len(taken), 2)
        self.assertEqual(len(new_bag.tiles), len(self.initial_tiles) - 2)
        
        # Test taking more tiles than available
        empty_bag = BagState(tuple())
        final_bag, no_tiles = BagOperations.take(empty_bag, 1, mock_random)
        self.assertEqual(no_tiles, tuple())
        self.assertEqual(final_bag.tiles, tuple())

    def test_used_tiles_operations(self):
        used = UsedTilesState(tuple())
        
        # Test giving tiles
        new_used = UsedTilesOperations.give(used, (Tile.RED, Tile.BLUE))
        self.assertEqual(new_used.tiles, (Tile.RED, Tile.BLUE))
        
        # Test taking all tiles
        empty_used, taken = UsedTilesOperations.take_all(new_used)
        self.assertEqual(taken, (Tile.RED, Tile.BLUE))
        self.assertEqual(empty_used.tiles, tuple())

    def test_table_area_operations(self):
        # Create initial game state
        factories = (
            Factory((Tile.RED, Tile.BLUE, Tile.RED, Tile.YELLOW)),
            Factory((Tile.BLACK, Tile.WHITE, Tile.BLACK, Tile.BLUE))
        )
        table_center = TableCenter((Tile.STARTING_PLAYER,))
        
        state = TableAreaState(
            factories=factories,
            table_center=table_center,
            bag=self.bag_state,
            used_tiles=self.used_tiles_state
        )
        
        # Test taking tiles from factory
        new_state, taken = TableAreaOperations.take_tiles(state, 0, 0)  # Take RED from first factory
        self.assertEqual(taken, (Tile.RED, Tile.RED))
        self.assertEqual(len(new_state.factories[0].tiles), 2)
        
        # Test round end detection
        self.assertFalse(TableAreaOperations.is_round_end(state))
        
        empty_state = TableAreaState(
            factories=(Factory(tuple()), Factory(tuple())),
            table_center=TableCenter(tuple()),
            bag=self.bag_state,
            used_tiles=self.used_tiles_state
        )
        self.assertTrue(TableAreaOperations.is_round_end(empty_state))

    def test_start_new_round(self):
        # Test starting new round with sufficient tiles in bag
        initial_state = TableAreaState(
            factories=(Factory(tuple()), Factory(tuple())),
            table_center=TableCenter(tuple()),
            bag=self.bag_state,
            used_tiles=self.used_tiles_state
        )
        
        # Create a sequence of random numbers that will work for the number of factories
        # Each factory needs 4 tiles, so we need 4 random numbers per factory
        sequence = [0, 1, 2, 3] * len(initial_state.factories)
        mock_random = MockRandomGenerator(sequence)
        
        new_state = TableAreaOperations.start_new_round(initial_state, mock_random)
        
        # Verify factories are refilled
        self.assertEqual(len(new_state.factories), len(initial_state.factories))
        for factory in new_state.factories:
            self.assertEqual(len(factory.tiles), 4)
            
        # Test starting new round with insufficient tiles in bag
        small_bag = BagState((Tile.RED, Tile.BLUE))  # Not enough tiles
        used_tiles = UsedTilesState((Tile.YELLOW, Tile.BLACK, Tile.WHITE))
        
        state_with_small_bag = TableAreaState(
            factories=(Factory(tuple()), Factory(tuple())),
            table_center=TableCenter(tuple()),
            bag=small_bag,
            used_tiles=used_tiles
        )
        
        sequence = [0, 1, 2, 3, 4] * len(initial_state.factories)
        mock_random = MockRandomGenerator(sequence)
        new_state = TableAreaOperations.start_new_round(state_with_small_bag, mock_random)
        
        # Verify tiles were moved from used tiles to bag
        self.assertEqual(len(new_state.used_tiles.tiles), 0)

if __name__ == '__main__':
    unittest.main()