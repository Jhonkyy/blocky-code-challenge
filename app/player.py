"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the player class hierarchy.
"""

import random
from typing import Optional
import pygame
from app.renderer import Renderer
from app.block import Block
from app.goal import Goal

TIME_DELAY = 600


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    renderer:
        The object that draws our Blocky board on the screen
        and tracks user interactions with the Blocky board.
    id:
        This player's number.  Used by the renderer to refer to the player,
        for example as "Player 2"
    goal:
        This player's assigned goal for the game.
    """
    renderer: Renderer
    id: int
    goal: Goal

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.renderer = renderer
        self.id = player_id

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """A human player.

    A HumanPlayer can do a limited number of smashes.

    === Public Attributes ===
    num_smashes:
        number of smashes which this HumanPlayer has performed
    === Representation Invariants ===
    num_smashes >= 0
    """
    # === Private Attributes ===
    # _selected_block
    #     The Block that the user has most recently selected for action;
    #     changes upon movement of the cursor and use of arrow keys
    #     to select desired level.
    # _level:
    #     The level of the Block that the user selected
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0

    # The total number of 'smash' moves a HumanPlayer can make during a game.
    MAX_SMASHES = 1

    num_smashes: int
    _selected_block: Optional[Block]
    _level: int

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        super().__init__(renderer, player_id, goal)
        self.num_smashes = 0

        # This HumanPlayer has done no smashes yet.
        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._selected_block = None

    def process_event(self, board: Block,
                      event: pygame.event.Event) -> Optional[int]:
        """Process the given pygame <event>.

        Identify the selected block and mark it as highlighted.  Then identify
        what it is that <event> indicates needs to happen to <board>
        and do it.

        Return
           - None if <event> was not a board-changing move (that is, if was
             a change in cursor position, or a change in _level made via
            the arrow keys),
           - 1 if <event> was a successful move, and
           - 0 if <event> was an unsuccessful move (for example in the case of
             trying to smash in an invalid location or when the player is not
             allowed further smashes).
        """
        # Get the new "selected" block from the position of the cursor
        block = board.get_selected_block(pygame.mouse.get_pos(), self._level)

        # Remove the highlighting from the old "_selected_block"
        # before highlighting the new one
        if self._selected_block is not None:
            self._selected_block.highlighted = False
        self._selected_block = block
        self._selected_block.highlighted = True

        # Since get_selected_block may have not returned the block at
        # the requested level (due to the level being too low in the tree),
        # set the _level attribute to reflect the level of the block which
        # was actually returned.
        self._level = block.level

        if event.type == pygame.MOUSEBUTTONDOWN:
            block.rotate(event.button)
            return 1
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if block.parent is not None:
                    self._level -= 1
                return None

            elif event.key == pygame.K_DOWN:
                if len(block.children) != 0:
                    self._level += 1
                return None

            elif event.key == pygame.K_h:
                block.swap(0)
                return 1

            elif event.key == pygame.K_v:
                block.swap(1)
                return 1

            elif event.key == pygame.K_s:
                if self.num_smashes >= self.MAX_SMASHES:
                    print('Can\'t smash again!')
                    return 0
                if block.smash():
                    self.num_smashes += 1
                    return 1
                else:
                    print('Tried to smash at an invalid depth!')
                    return 0

    def make_move(self, board: Block) -> int:
        """Choose a move to make on the given board, and apply it, mutating
        the Board as appropriate.

        Return 0 upon successful completion of a move, and 1 upon a QUIT event.

        This method will hold focus until a valid move is performed.
        """
        self._level = 0
        self._selected_block = board

        # Remove all previous events from the queue in case the other players
        # have added events to the queue accidentally.
        pygame.event.clear()

        # Keep checking the moves performed by the player until a valid move
        # has been completed. Draw the board on every loop to draw the
        # selected block properly on screen.
        while True:
            self.renderer.draw(board, self.id)
            # loop through all of the events within the event queue
            # (all pending events from the user input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 1

                result = self.process_event(board, event)
                self.renderer.draw(board, self.id)
                if result is not None and result > 0:
                    # un-highlight the selected block
                    self._selected_block.highlighted = False
                    return 0


class RandomPlayer(Player):
    """A random player that makes random moves."""

    def make_move(self, board: Block) -> int:
        """Choose a random move on the given board and apply it."""
        import random

        # Choose a random block
        block = board.get_selected_block(
            (random.randint(0, board.size), random.randint(0, board.size)),
            random.randint(0, board.max_depth)
        )

        # Highlight the block and draw the board
        block.highlighted = True
        self.renderer.draw(board, self.id)
        pygame.time.wait(TIME_DELAY)

        # Choose a random action
        action = random.choice(["rotate_cw", "rotate_ccw", "swap_h", "swap_v", "smash"])
        if action == "rotate_cw":
            block.rotate(1)
        elif action == "rotate_ccw":
            block.rotate(3)
        elif action == "swap_h":
            block.swap(0)
        elif action == "swap_v":
            block.swap(1)
        elif action == "smash" and block.smash():
            pass  # Smash is applied only if valid

        # Remove highlight and redraw the board
        block.highlighted = False
        self.renderer.draw(board, self.id)
        return 0


class SmartPlayer(Player):
    """A smart player that evaluates moves and chooses the best one."""

    def __init__(self, renderer: Renderer, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize this SmartPlayer with the given difficulty level."""
        super().__init__(renderer, player_id, goal)
        self.difficulty = difficulty

    def make_move(self, board: Block) -> int:
        """Evaluate possible moves and choose the best one."""
        import random

        # Determine the number of moves to evaluate based on difficulty
        moves_to_evaluate = min(150, [5, 10, 25, 50, 100, 150][min(self.difficulty, 5)])
        best_score = -1
        best_move = None
        best_block = None

        for _ in range(moves_to_evaluate):
            # Choose a random block
            block = board.get_selected_block(
                (random.randint(0, board.size), random.randint(0, board.size)),
                random.randint(0, board.max_depth)
            )

            # Choose a random action (excluding smash)
            action = random.choice(["rotate_cw", "rotate_ccw", "swap_h", "swap_v"])
            original_state = board.flatten()

            # Apply the action
            if action == "rotate_cw":
                block.rotate(1)
            elif action == "rotate_ccw":
                block.rotate(3)
            elif action == "swap_h":
                block.swap(0)
            elif action == "swap_v":
                block.swap(1)

            # Evaluate the score
            score = self.goal.score(board)

            # Undo the action
            board.update_block_locations((0, 0), board.size)
            for i, row in enumerate(original_state):
                for j, colour in enumerate(row):
                    board.flatten()[i][j] = colour

            # Keep track of the best move
            if score > best_score:
                best_score = score
                best_move = action
                best_block = block

        # Apply the best move
        if best_block:
            best_block.highlighted = True
            self.renderer.draw(board, self.id)
            pygame.time.wait(TIME_DELAY)

            if best_move == "rotate_cw":
                best_block.rotate(1)
            elif best_move == "rotate_ccw":
                best_block.rotate(3)
            elif best_move == "swap_h":
                best_block.swap(0)
            elif best_move == "swap_v":
                best_block.swap(1)

            best_block.highlighted = False
            self.renderer.draw(board, self.id)

        return 0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer',
            'pygame'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
