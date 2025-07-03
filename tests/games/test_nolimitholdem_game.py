import unittest

from rlcard.games.limitholdem.player import PlayerStatus
from rlcard.games.nolimitholdem.game import NolimitholdemGame as Game, Stage
import numpy as np
from rlcard.utils import seeding

from rlcard.games.nolimitholdem.round import Action


class TestNolimitholdemMethods(unittest.TestCase):

    def test_init_game(self):
        game = Game()
        state, player_id = game.init_game()
        test_id = game.get_player_id()
        self.assertEqual(test_id, player_id)

    def test_step(self):
        game = Game()

        # test call
        game.init_game()
        init_not_raise_num = game.round.not_raise_num
        game.step(Action.CHECK_CALL)
        step_not_raise_num = game.round.not_raise_num
        self.assertEqual(init_not_raise_num + 1, step_not_raise_num)

        # test fold
        _, player_id = game.init_game()
        game.step(Action.FOLD)

        self.assertEqual(PlayerStatus.FOLDED, game.players[player_id].status)

        # test check
        game.init_game()
        game.step(Action.CHECK_CALL)

    def test_bet_more_than_chips(self):
        game = Game()

        # test check
        game.init_game()
        player = game.players[0]
        in_chips = player.in_chips
        player.bet(50)
        self.assertEqual(50+in_chips, player.in_chips)

        player.bet(150)
        self.assertEqual(100, player.in_chips)

    def test_step_2(self):
        game = Game()

        # test check
        game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.FLOP, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.TURN, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.RIVER, game.stage)

    def test_step_3_players(self):
        game = Game(num_players=3)

        # test check
        _, first_player_id = game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.FOLD)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.FLOP, game.stage)
        self.assertEqual((first_player_id - 2) % 3, game.round.game_pointer)
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.TURN, game.stage)
        self.assertEqual((first_player_id - 2) % 3, game.round.game_pointer)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.RIVER, game.stage)

    def test_auto_step(self):
        game = Game()

        game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage)
        game.step(Action.ALL_IN)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.RIVER, game.stage)

    def test_all_in(self):
        game = Game()

        _, player_id = game.init_game()
        game.step(Action.ALL_IN)
        step_raised = game.round.raised[player_id]
        self.assertEqual(100, step_raised)
        self.assertEqual(100, game.players[player_id].in_chips)
        self.assertEqual(0, game.players[player_id].remained_chips)

    def test_all_in_rounds(self):
        game = Game()

        game.init_game()
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)
        self.assertEqual(game.round_counter, 1)

        game.step(Action.CHECK_CALL)
        game.step(Action.ALL_IN)
        self.assertListEqual([Action.FOLD, Action.CHECK_CALL], game.get_legal_actions())
        game.step(Action.CHECK_CALL)
        self.assertEqual(game.round_counter, 4)
        self.assertEqual(200, game.dealer.pot)

    def test_raise_pot(self):
        game = Game()

        _, player_id = game.init_game()
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(4, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(8, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(16, step_raised)

        game.step(Action.CHECK_CALL)
        player_id = game.round.game_pointer
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(32, step_raised)

    def test_raise_half_pot(self):
        game = Game()

        _, player_id = game.init_game()
        self.assertNotIn(Action.RAISE_HALF_POT, game.get_legal_actions()) # Half pot equals call
        game.step(Action.CHECK_CALL)
        step_raised = game.round.raised[player_id]
        self.assertEqual(2, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_HALF_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(4, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_HALF_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(5, step_raised)

    def test_payoffs_1(self):
        game = Game()
        game.init_game()
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_HALF_POT)
        game.step(Action.FOLD)
        self.assertTrue(game.is_over())
        self.assertEqual(2, len(game.get_payoffs()))
        #self.assertListEqual([-2.0, 2.0], game.get_payoffs())

    def test_payoffs_2(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.ALL_IN)
        game.step(Action.FOLD)
        self.assertTrue(game.is_over())
        self.assertEqual(2, len(game.get_payoffs()))
        #self.assertListEqual([6.0, -6.0], game.get_payoffs())

    def test_all_in_to_call(self):
        game = Game()
        game.init_chips = [50, 100]
        game.dealer_id = 0
        game.init_game()
        game.step(Action.CHECK_CALL)
        game.step(Action.ALL_IN)
        game.step(Action.CHECK_CALL)
        self.assertTrue(game.is_over())

    def test_heads_up_acting_order(self):
        """Test that heads-up poker has correct acting order post-flop."""
        game = Game(num_players=2)
        game.dealer_id = 0
        
        # Initialize the game
        state, first_player = game.init_game()
        
        # Pre-flop: Small blind (dealer in heads-up) should act first
        expected_preflop_first = (game.dealer_id + 1) % 2  # Small blind
        self.assertEqual(first_player, expected_preflop_first)
        
        # Play through pre-flop
        game.step(Action.CHECK_CALL)  # Small blind calls
        game.step(Action.CHECK_CALL)  # Big blind checks
        
        # Should now be at flop
        self.assertEqual(game.stage, Stage.FLOP)
        
        # Post-flop: Big blind should act first in heads-up
        current_player = game.game_pointer
        expected_postflop_first = (game.dealer_id + 2) % 2  # Big blind
        self.assertEqual(current_player, expected_postflop_first)
        
        # Continue to next round to verify it persists
        game.step(Action.CHECK_CALL)  # Big blind checks
        game.step(Action.CHECK_CALL)  # Small blind checks
        
        # Should now be at turn
        self.assertEqual(game.stage, Stage.TURN)
        
        # Turn: Big blind should still act first
        current_player = game.game_pointer
        self.assertEqual(current_player, expected_postflop_first)

    def test_multi_player_acting_order_unchanged(self):
        """Test that multi-player poker acting order is unchanged."""
        game = Game(num_players=3)
        game.dealer_id = 0
        
        # Initialize the game
        state, first_player = game.init_game()
        
        # Pre-flop: Player after big blind should act first
        expected_preflop_first = (game.dealer_id + 3) % 3  # Player after big blind
        self.assertEqual(first_player, expected_preflop_first)
        
        # Play through pre-flop
        game.step(Action.CHECK_CALL)  # Player 0 calls
        game.step(Action.CHECK_CALL)  # Small blind calls
        game.step(Action.CHECK_CALL)  # Big blind checks
        
        # Should now be at flop
        self.assertEqual(game.stage, Stage.FLOP)
        
        # Post-flop: Small blind should act first (if still in hand)
        current_player = game.game_pointer
        expected_postflop_first = (game.dealer_id + 1) % 3  # Small blind
        self.assertEqual(current_player, expected_postflop_first)


if __name__ == '__main__':
    unittest.main()
