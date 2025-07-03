# Heads-Up Poker Acting Order Fix

## Problem
The Texas No Limit Hold'em implementation in RLCard had incorrect acting order for heads-up poker (2 players). According to standard poker rules:

- **Pre-flop**: Small blind (dealer in heads-up) acts first
- **Post-flop**: Small blind acts LAST (big blind acts first)

However, the original implementation made the small blind act first in all betting rounds, which is incorrect for heads-up play.

## Solution
Modified the `step()` method in `/rlcard/games/nolimitholdem/game.py` to correctly handle heads-up poker acting order:

### Changes Made
1. **File**: `rlcard/games/nolimitholdem/game.py`
   - **Lines 160-165**: Added logic to differentiate between heads-up and multi-player games
   - **Heads-up (2 players)**: Big blind acts first in all post-flop rounds
   - **Multi-player (3+ players)**: Small blind acts first post-flop (unchanged behavior)

### Code Changes
```python
# Before (lines 157-161)
if self.round.is_over():
    self.game_pointer = (self.dealer_id + 1) % self.num_players  # Always small blind first

# After (lines 160-165)
if self.round.is_over():
    if self.num_players == 2:
        # Heads-up: big blind acts first in all post-flop rounds
        self.game_pointer = (self.dealer_id + 2) % self.num_players
    else:
        # Multi-player: small blind acts first post-flop
        self.game_pointer = (self.dealer_id + 1) % self.num_players
```

## Testing
Added comprehensive tests to verify the fix:

1. **New test methods** in `tests/games/test_nolimitholdem_game.py`:
   - `test_heads_up_acting_order()`: Verifies correct heads-up acting order
   - `test_multi_player_acting_order_unchanged()`: Ensures multi-player games are unaffected

2. **All existing tests pass**: Confirmed backward compatibility

## Verification
- ✅ Heads-up pre-flop: Small blind acts first
- ✅ Heads-up post-flop: Big blind acts first (small blind acts last)
- ✅ Multi-player games: Unchanged behavior (small blind acts first post-flop)
- ✅ All existing functionality preserved
- ✅ Environment integration works correctly

## Impact
- **Heads-up poker**: Now follows correct poker rules
- **Multi-player poker**: No changes (maintains existing behavior)
- **Backward compatibility**: All existing code and tests continue to work
- **Performance**: No performance impact

This fix ensures that RLCard's Texas No Limit Hold'em implementation correctly follows standard poker rules for heads-up play while maintaining full compatibility with existing multi-player games.