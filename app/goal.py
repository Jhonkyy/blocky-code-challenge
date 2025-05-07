"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Goal class hierarchy.
"""

from typing import List, Tuple
from app.block import Block


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def score(self, board: Block) -> int:
        """Return the score for this goal on the given board."""
        flattened = board.flatten()
        visited = [[-1 for _ in range(len(flattened))] for _ in range(len(flattened))]
        max_blob_size = 0

        for i in range(len(flattened)):
            for j in range(len(flattened)):
                if visited[i][j] == -1:  # Not visited
                    blob_size = self._undiscovered_blob_size((i, j), flattened, visited)
                    max_blob_size = max(max_blob_size, blob_size)

        return max_blob_size

    def description(self) -> str:
        """Return a description of this goal."""
        return "Create the largest connected blob of the target colour."

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
           -1  if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        x, y = pos
        if not (0 <= x < len(board) and 0 <= y < len(board)):
            return 0
        if visited[x][y] != -1:
            return 0
        if board[x][y] != self.colour:
            visited[x][y] = 0
            return 0

        visited[x][y] = 1
        size = 1  # Count this cell
        # Check neighbors (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            size += self._undiscovered_blob_size((x + dx, y + dy), board, visited)

        return size


class PerimeterGoal(Goal):
    """A goal to maximize the number of unit cells of the target colour
    on the outer perimeter of the board.
    """

    def score(self, board: Block) -> int:
        """
        Calculate the score for this goal based on the number of unit cells
        of the target colour that are on the perimeter of the board.
        """
        flattened = board.flatten()
        size = len(flattened)
        count = 0

        # Revisar los bordes superior e inferior
        for i in range(size):
            if flattened[0][i] == self.colour:  # Borde superior
                count += 1
            if flattened[size - 1][i] == self.colour:  # Borde inferior
                count += 1

        # Revisar los bordes izquierdo y derecho
        for i in range(size):
            if flattened[i][0] == self.colour:  # Borde izquierdo
                count += 1
            if flattened[i][size - 1] == self.colour:  # Borde derecho
                count += 1

        return count

    def description(self) -> str:
        """Return a description of this goal."""
        return "Maximize the number of unit cells of the target colour on the perimeter."


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer'
        ],
        'max-attributes': 15
    })
