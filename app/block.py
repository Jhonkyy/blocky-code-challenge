"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Block class, the main data structure used in the game.
"""
from typing import Optional, Tuple, List
import random
import math
from app.renderer import COLOUR_LIST, TEMPTING_TURQUOISE, BLACK, colour_name


HIGHLIGHT_COLOUR = TEMPTING_TURQUOISE
FRAME_COLOUR = BLACK


class Block:
    """A square block in the Blocky game.

    === Public Attributes ===
    position:
        The (x, y) coordinates of the upper left corner of this Block.
        Note that (0, 0) is the top left corner of the window.
    size:
        The height and width of this Block.  Since all blocks are square,
        we needn't represent height and width separately.
    colour:
        If this block is not subdivided, <colour> stores its colour.
        Otherwise, <colour> is None and this block's sublocks store their
        individual colours.
    level:
        The level of this block within the overall block structure.
        The outermost block, corresponding to the root of the tree,
        is at level zero.  If a block is at level i, its children are at
        level i+1.
    max_depth:
        The deepest level allowed in the overall block structure.
    highlighted:
        True iff the user has selected this block for action.
    children:
        The blocks into which this block is subdivided.  The children are
        stored in this order: upper-right child, upper-left child,
        lower-left child, lower-right child.
    parent:
        The block that this block is directly within.

    === Representation Invariations ===
    - len(children) == 0 or len(children) == 4
    - If this Block has children,
        - their max_depth is the same as that of this Block,
        - their size is half that of this Block,
        - their level is one greater than that of this Block,
        - their position is determined by the position and size of this Block,
          as defined in the Assignment 2 handout, and
        - this Block's colour is None
    - If this Block has no children,
        - its colour is not None
    - level <= max_depth
    """
    position: Tuple[int, int]
    size: int
    colour: Optional[Tuple[int, int, int]]
    level: int
    max_depth: int
    highlighted: bool
    children: List['Block']
    parent: Optional['Block']

    def __init__(self, level: int,
                 colour: Optional[Tuple[int, int, int]] = None,
                 children: Optional[List['Block']] = None) -> None:
        """Initialize this Block to be an unhighlighted root block with
        no parent.

        If <children> is None, give this block no children.  Otherwise
        give it the provided children.  Use the provided level and colour,
        and set everything else (x and y coordinates, size,
        and max_depth) to 0.  (All attributes can be updated later, as
        appropriate.)
        """
        self.position = (0, 0)
        self.size = 0
        self.level = level
        self.max_depth = 0
        self.highlighted = False
        self.parent = None

        if children is None:
            self.children = []
            self.colour = colour
        else:
            self.children = children
            self.colour = None
            for child in self.children:
                child.parent = self

    def rectangles_to_draw(self) -> List[Tuple[Tuple[int, int, int],
                                               Tuple[int, int],
                                               Tuple[int, int],
                                               int]]:
        """
        Return a list of tuples describing all of the rectangles to be drawn
        in order to render this Block.

        This includes (1) for every undivided Block:
            - one rectangle in the Block's colour
            - one rectangle in the FRAME_COLOUR to frame it at the same
              dimensions, but with a specified thickness of 3
        and (2) one additional rectangle to frame this Block in the
        HIGHLIGHT_COLOUR at a thickness of 5 if this block has been
        selected for action, that is, if its highlighted attribute is True.

        The rectangles are in the format required by method Renderer.draw.
        Each tuple contains:
        - the colour of the rectangle
        - the (x, y) coordinates of the top left corner of the rectangle
        - the (height, width) of the rectangle, which for our Blocky game
          will always be the same
        - an int indicating how to render this rectangle. If 0 is specified
          the rectangle will be filled with its colour. If > 0 is specified,
          the rectangle will not be filled, but instead will be outlined in
          the FRAME_COLOUR, and the value will determine the thickness of
          the outline.

        The order of the rectangles does not matter.
        """
        rects = []
        x, y = self.position
        size = self.size

        if not self.children:
            # Agregar el rectángulo del color del bloque
            rects.append((self.colour, (x, y), (size, size), 0))
            # Agregar el marco del bloque
            rects.append((FRAME_COLOUR, (x, y), (size, size), 3))
        else:
            # Recursivamente agregar los rectángulos de los hijos
            for child in self.children:
                rects.extend(child.rectangles_to_draw())

        if self.highlighted:
            # Agregar el marco de resaltado si el bloque está resaltado
            rects.append((HIGHLIGHT_COLOUR, (x, y), (size, size), 5))

        return rects

    def swap(self, direction: int) -> None:
        """Swap the child Blocks of this Block.

        If <direction> is 1, swap vertically. If <direction> is 0, swap
        horizontally. If this Block has no children, do nothing.
        """
        if not self.children:
            return

        if direction == 0:  # Horizontal swap
            self.children[0], self.children[1] = self.children[1], self.children[0]
            self.children[2], self.children[3] = self.children[3], self.children[2]
        elif direction == 1:  # Vertical swap
            self.children[0], self.children[2] = self.children[2], self.children[0]
            self.children[1], self.children[3] = self.children[3], self.children[1]

        self.update_block_locations(self.position, self.size)

    def rotate(self, direction: int) -> None:
        """Rotate this Block and all its descendants."""
        if not self.children:
            return

        # Reordenar los hijos según la dirección de rotación
        if direction == 1:  # Rotación en sentido horario
            self.children = [self.children[3], self.children[0], self.children[1], self.children[2]]
        elif direction == 3:  # Rotación en sentido antihorario
            self.children = [self.children[1], self.children[2], self.children[3], self.children[0]]

        # Actualizar las posiciones y tamaños de los bloques hijos
        self.update_block_locations(self.position, self.size)

        # Aplicar la rotación recursivamente a los hijos
        for child in self.children:
            child.rotate(direction)

    def smash(self) -> bool:
        """Smash this block.

        If this Block can be smashed, randomly generate four new child Blocks
        for it. If it already had child Blocks, discard them. Ensure that the
        RI's of the Blocks remain satisfied.

        A Block can be smashed iff it is not the top-level Block and it
        is not already at the level of the maximum depth.

        Return True if this Block was smashed and False otherwise.
        """
        if self.parent is None or self.level == self.max_depth:
            return False

        self.children = []
        for _ in range(4):
            child = Block(self.level + 1, random.choice(COLOUR_LIST))
            child.max_depth = self.max_depth
            child.parent = self
            self.children.append(child)

        self.colour = None
        self.update_block_locations(self.position, self.size)
        return True

    def update_block_locations(self, top_left: Tuple[int, int],
                               size: int) -> None:
        """
        Update the position and size of each of the Blocks within this Block.

        Ensure that each is consistent with the position and size of its
        parent Block.

        <top_left> is the (x, y) coordinates of the top left corner of
        this Block.  <size> is the height and width of this Block.
        """
        self.position = top_left
        self.size = size

        if self.children:
            half = size // 2

            positions = [
                (top_left[0] + half, top_left[1]),  # Arriba derecha
                (top_left[0], top_left[1]),  # Arriba izquierda
                (top_left[0], top_left[1] + half),  # Abajo izquierda
                (top_left[0] + half, top_left[1] + half)  # Abajo derecha
            ]


            for child, pos in zip(self.children, positions):
                child.update_block_locations(pos, half)

    def get_selected_block(self, location: Tuple[int, int], level: int) -> 'Block':
        """Return the Block within this Block that includes the given location
        and is at the given level."""
        x, y = location
        if level == self.level or not self.children:
            return self
        half = self.size // 2
        if x >= self.position[0] + half:
            if y >= self.position[1] + half:
                return self.children[3].get_selected_block(location, level)  # Lower-right
            else:
                return self.children[0].get_selected_block(location, level)  # Upper-right
        else:
            if y >= self.position[1] + half:
                return self.children[2].get_selected_block(location, level)  # Lower-left
            else:
                return self.children[1].get_selected_block(location, level)  # Upper-left

    def flatten(self) -> List[List[Tuple[int, int, int]]]:
        """Return a two-dimensional list representing this Block as rows
        and columns of unit cells.

        Return a list of lists L, where,
        for 0 <= i, j < 2^{max_depth - self.level}
            - L[i] represents column i and
            - L[i][j] represents the unit cell at column i and row j.
        Each unit cell is represented by 3 ints for the colour
        of the block at the cell location[i][j]

        L[0][0] represents the unit cell in the upper left corner of the Block.
        """
        size = int(2 ** (self.max_depth - self.level))  # Asegurar que size sea un entero
        if not self.children:
            # Si no tiene hijos, llenar con el color del bloque
            return [[self.colour] * size for _ in range(size)]
        else:
            # Combinar las matrices de los hijos
            top = [self.children[1].flatten(), self.children[0].flatten()]
            bottom = [self.children[2].flatten(), self.children[3].flatten()]
            return [
                top[0][i] + top[1][i] for i in range(size // 2)
            ] + [
                bottom[0][i] + bottom[1][i] for i in range(size // 2)
            ]


def random_init(level: int, max_depth: int) -> 'Block':
    """Return a randomly-generated Block with level <level> and subdivided
    to a maximum depth of <max_depth>.

    Throughout the generated Block, set appropriate values for all attributes
    except position and size.  They can be set by the client, using method
    update_block_locations.

    Precondition:
        level <= max_depth
    """
    if level == max_depth or random.random() > 0.5:
        # Crear un bloque sin hijos con un color aleatorio
        return Block(level, random.choice(COLOUR_LIST))
    else:
        # Crear un bloque con cuatro hijos
        children = [random_init(level + 1, max_depth) for _ in range(4)]
        return Block(level, children=children)


def attributes_str(b: Block, verbose) -> str:
    """Return a str that is a concise representation of the attributes of <b>.
    Precondition: b is not None.
    """
    print_block_indented(b, 0, verbose)


def print_block_indented(b: Block, indent: int, verbose) -> None:
    """Print a text representation of Block <b>, indented <indent> steps.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Precondition: b is not None.
    """
    if len(b.children) == 0:
        # b a leaf.  Print its colour and other attributes
        print(f'{"  " * indent}{colour_name(b.colour)}: ' +
              f'{attributes_str(b, verbose)}')
    else:
        # b is not a leaf, so it doesn't have a colour.  Print its
        # other attributes.  Then print its children.
        print(f'{"  " * indent}{attributes_str(b, verbose)}')
        for child in b.children:
            print_block_indented(child, indent + 1, verbose)

if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'allowed-io': ['print_block_indented'],
    #     'allowed-import-modules': [
    #         'doctest', 'python_ta', 'random', 'typing',
    #         'block', 'goal', 'player', 'renderer', 'math'
    #     ],
    #     'max-attributes': 15
    # })

    # This tiny tree with one node will have no children, highlighted False,
    # and will have the provided values for level and colour; the initializer
    # sets all else (position, size, and max_depth) to 0.
    b0 = Block(0, COLOUR_LIST[2])
    # Now we update position and size throughout the tree.
    b0.update_block_locations((0, 0), 750)
    print("=== tiny tree ===")
    # We have not set max_depth to anything meaningful, so it still has the
    # value given by the initializer (0 and False).
    print_block(b0, True)

    b1 = Block(0, children=[
        Block(1, children=[
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, COLOUR_LIST[2]),
        Block(1, children=[
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, children=[
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[1])
        ])
    ])
    b1.update_block_locations((0, 0), 750)
    print("\n=== handmade tree ===")
    # Similarly, max_depth is still 0 in this tree.  This violates the
    # representation invariants of the class, so we shouldn't use such a
    # tree in our real code, but we can use it to see what print_block
    # does with a slightly bigger tree.
    print_block(b1, True)

    # Now let's make a random tree.
    # random_init has the job of setting all attributes except position and
    # size, so this time max_depth is set throughout the tree to the provided
    # value (3 in this case).
    b2 = random_init(0, 3)
    # Now we update position and size throughout the tree.
    b2.update_block_locations((0, 0), 750)
    print("\n=== random tree ===")
    # All attributes should have sensible values when we print this tree.
    print_block(b2, True)
