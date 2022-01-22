import numpy as np
import math
import enum


class Tetrominoes(enum.Enum):
    J = 1
    L = 2
    O = 3
    I = 4
    T = 5
    S = 6
    Z = 7


blockpos_from_tetromino = {
        Tetrominoes.J: [[0, 0], [-1, -1], [-1, 0], [1, 0]],
        Tetrominoes.L: [[0, 0], [-1, 0], [1, 0], [1, -1]],
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
        self._blocks = np.array(blockpos_from_tetromino[self._type],
                                dtype=float)
        self.rotation_state = 0

        # Center is standard, except for I and O
        self._center = [0, 0]
        if type_ == Tetrominoes.O or type_ == Tetrominoes.I:
            self._center = [-0.5, -0.5]

    def move(self, transl=[0, 0], rotdeg=0, set_=True):
        """Moves the piece by translation and/or rotation.

        :direction: TODO
        :returns: TODO

        """

        # With set_, the class variables are set. Otherwise returned
        if set_:
            center = self._center
            blocks = self._blocks
        else:
            center = self._center.copy()
            blocks = self._blocks.copy()

        # Translate the block
        if np.any(transl):
            center[0] += transl[0]
            center[1] += transl[1]

        # Rotate the block
        if rotdeg != 0:
            rot = math.radians(rotdeg)
            x = blocks[:, 0].copy()
            y = blocks[:, 1].copy()
            # Round to avoid calculation errors
            blocks[:, 0] = (x*math.cos(rot) - y*math.sin(rot)).round(4)
            blocks[:, 1] = (x*math.sin(rot) + y*math.cos(rot)).round(4)

        if set_:
            return None
        else:
            return center, blocks

    def get_blocks(self, transl=[0, 0], rotdeg=0):
        """TODO: Docstring for get_blocks.
        :returns: TODO

        """
        if np.any(transl) or rotdeg != 0:
            center, blocks = self.move(transl, rotdeg, set_=False)
        else:
            center = self._center
            blocks = self._blocks

        # Calculate the blocks relative to center
        bl = blocks.copy()
        bl[:, 0] += center[0]
        bl[:, 1] += center[1]

        return bl.astype(int)
