from enum import Enum
import numpy as np
import math

class Tetrominoes(Enum):
    J = 1
    L = 2
    O = 3
    I = 4
    T = 5
    S = 6
    Z = 7

blocks_from_tetromino = \
        {
        Tetrominoes.J: [[0, 0], [0, -1], [0, 1], [-1, 1]],
        Tetrominoes.L: [[0, -1], [0, 0], [0, 1], [1, 1]],
        Tetrominoes.O: [[-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5], [0.5, 0.5]],
        Tetrominoes.I: [[0.5, -1.5], [0.5, -0.5], [0.5, 0.5], [0.5, 1.5]],
        Tetrominoes.T: [[0, 0], [0, -1], [-1, 0], [1, 0]],
        Tetrominoes.S: [[0, 0], [-1, 0], [0, -1], [1, -1]],
        Tetrominoes.Z: [[0, 0], [-1, -1], [0, -1], [1, 0]]
        }


class Tetromino(object):

    """Docstring for Tetromino. """

    def __init__(self, type_):
        """TODO: to be defined. """
        self._type = type_
        self._blocks = np.array(blocks_from_tetromino[self._type], dtype=float)

        self._center = [0, 0]
        if type_ == Tetrominoes.O or type_ == Tetrominoes.I:
            self._center = [-0.5, -0.5]

    def move(self, direction):
        """TODO: Docstring for move.

        :direction: TODO
        :returns: TODO

        """
        self._center[0] += direction[0]
        self._center[1] += direction[1]

    def rotate(self, rot):
        """TODO: Docstring for rotate.

        :direction: TODO
        :returns: TODO

        """
        rot = math.radians(rot)
        x = self._blocks[:, 0].copy()
        y = self._blocks[:, 1].copy()
        # Round to avoid calculation errors
        self._blocks[:, 0] = (x*math.cos(rot) - y*math.sin(rot)).round(4)
        self._blocks[:, 1] = (x*math.sin(rot) + y*math.cos(rot)).round(4)

    def get_blocks(self):
        """TODO: Docstring for get_blocks.
        :returns: TODO

        """
        bl = self._blocks.copy()
        bl[:, 0] += self._center[0]
        bl[:, 1] += self._center[1]
        return bl.astype(int)

    blocks = property(get_blocks)
