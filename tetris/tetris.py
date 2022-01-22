import numpy as np
import tetromino
import random


SRS_Rotation = {
        'normal': {
            0: {1: [[-1, 0], [-1, 1], [0, -2], [-1, -2]],
                3: [[1, 0], [1, 1], [0, -2], [1, -2]]},
            1: {0: [[1, 0], [1, -1], [0, 2], [1, 2]],
                2: [[1, 0], [1, -1], [0, 2], [1, 2]]},
            2: {1: [[-1, 0], [-1, 1], [0, -2], [-1, -2]],
                3: [[1, 0], [1, 1], [0, -2], [1, -2]]},
            3: {2: [[-1, 0], [-1, -1], [0, 2], [-1, 2]],
                0: [[-1, 0], [-1, -1], [0, 2], [-1, 2]]}
        },
        'I': {
            0: {1: [[-2, 0], [1, 0], [-2, -1], [1, 2]],
                3: [[-1, 0], [2, 0], [-1, 2], [2, -1]]},
            1: {0: [[2, 0], [-1, 0], [2, 1], [-1, -2]],
                2: [[-1, 0], [2, 0], [-1, 2], [2, -1]]},
            2: {1: [[1, 0], [-2, 0], [1, -2], [-2, 1]],
                3: [[2, 0], [-1, 0], [2, 1], [-1, -2]]},
            3: {2: [[-2, 0], [1, 0], [-2, -1], [1, 2]],
                0: [[1, 0], [-2, 0], [1, -2], [-2, 1]]}
        }
}


class Tetris(object):

    """Docstring for Tetris. """

    def __init__(self, width, height, queue_len=1):
        """TODO: to be defined.

        :width: TODO
        :height: TODO

        """
        self._width = width
        self._height = height
        self._board = np.zeros((self._width, self._height), dtype=int)
        self._active = None
        self._hold = None
        self._score = 0
        self._rows = 0
        self._queue = []
        self._queue_len = queue_len

    def _next_tetromino(self):
        """Gets the next Tetromino from queue and refills it up to queue_len.

        If the queue is empty, generate a random Tetromino.
        """
        # Empty queue, create a new Tetromino
        if len(self._queue) == 0:
            type_ = random.choice(list(tetromino.Tetrominoes))
            next_tetromino = tetromino.Tetromino(type_)
        else:
            next_tetromino = self._queue.pop(0)

        # Refill the queue
        for _ in range(self._queue_len - len(self._queue)):
            type_ = random.choice(list(tetromino.Tetrominoes))
            self._queue.append(tetromino.Tetromino(type_))

        return next_tetromino

    def hold_active(self):
        """
        """
        self._active.reset()
        if self._hold is None:
            self._hold = self._active
            self.spawn_tetromino()
        else:
            temp = self._hold
            self._hold = self._active
            self.spawn_tetromino(temp)

    def dist_to_bottom(self):
        """
        """
        blocks = self._active.get_blocks()
        # TODO: Make faster
        # Perhaps by precalculating all shortest distances when a tetromino is
        # spawned?
        shortest_dist = self._height
        for block in blocks:
            col = self._board[block[0], block[1]:]
            end_sites = np.where(col > 0)[0]
            if len(end_sites) == 0:
                end_site = self._height - block[1]
            else:
                end_site = end_sites[0]
            if end_site < shortest_dist:
                shortest_dist = end_site

        return shortest_dist - 1

    def hold_tetromino_blocks(self):
        """
        """
        if self._hold is None:
            yield None
        blocks = self._hold.get_blocks()
        val = self._hold._type.value
        for x, y in blocks:
            yield x, y, val

    # TODO: Fix function name and function
    def shadow_tetromino_blocks(self):
        """
        """
        blocks = self._active.get_blocks(transl=[0, self.dist_to_bottom()])
        val = self._active._type.value
        for x, y in blocks:
            yield x, y, val

    def tetromino_blocks(self, active=True, pos=0):
        """
        """
        if active:
            blocks = self._active.get_blocks()
            val = self._active._type.value
        else:
            blocks = self._queue[pos].get_blocks()
            val = self._queue[pos]._type.value

        for x, y in blocks:
            yield x, y, val

    def board_blocks(self):
        """Iterator to return the position and vals of filled blocks.

        :returns: Iterator with pos x, pos y and value
        """
        for i in range(self._height):
            for j in range(self._width):
                if self._board[j, i] != 0:
                    yield j, i, self._board[j, i]

    def spawn_tetromino(self, piece=None):
        """TODO: Docstring for add_tetromino.

        :f: TODO
        :returns: TODO

        """
        if piece is None:
            self._active = self._next_tetromino()
        else:
            self._active = piece
        # Initial placement is middle justified by tetromino height
        coll_id = self.move_active(transl=[int(self._width/2),
                                   -min(self._active.get_blocks()[:, 1])],
                                   force=True)
        if coll_id != 0:
            return False

        return True

    def game_tick(self):
        """TODO: Docstring for move_active.

        :direction: TODO
        :returns: TODO

        """
        coll_id = self.move_active(transl=[0, 1])

        return coll_id

    def move_active(self, transl=[0, 0], rotdeg=0, force=False):
        """
        """
        if np.any(transl) and rotdeg > 0:
            raise AttributeError('translation and rotation cannot occur' +
                                 'simultaneously')

        coll_id = self.move_collision(transl=transl, rotdeg=rotdeg)
        # Go through the SRS list
        if coll_id != 0 and rotdeg > 0:
            initial_state = self._active.get_state()
            new_state = self._active.new_state(rotdeg)
            srs_moves = []
            if self._active._type == tetromino.Tetrominoes.I:
                srs_moves = SRS_Rotation['I'][initial_state][new_state]
            elif self._active._type != tetromino.Tetrominoes.O:
                srs_moves = SRS_Rotation['normal'][initial_state][new_state]
            for move in srs_moves:
                coll_id = self.move_collision(transl=move, rotdeg=rotdeg)
                if coll_id == 0:
                    transl = move
                    break

        if coll_id == 0 or force:
            self._active.move(transl=transl, rotdeg=rotdeg)

        return coll_id

    def move_collision(self, transl=[0, 0], rotdeg=0):
        """Checks that a move does not lead to collision.

        :returns: 1 if edge collision, 2 if block collision, 0 if none
        """
        coll_id = 0
        blocks = self._active.get_blocks(transl=transl, rotdeg=rotdeg)
        # If going outside of game board
        if blocks[:, 0].min() < 0 or blocks[:, 0].max() >= self._width:
            coll_id = 1
        elif max(blocks[:, 1]) >= self._height:  # hits end
            coll_id = 2
        elif np.any(self._board[blocks[:, 0], blocks[:, 1]]):  # hits another
            coll_id = 2

        return coll_id

    def lock_active(self):
        """
        """
        blocks = self._active.get_blocks()
        self._board[blocks[:, 0], blocks[:, 1]] = self._active._type.value
        self._active = None

    def check_rows(self):
        """TODO: Docstring for _check_rows.
        :returns: TODO

        """
        # Get all filled y-rows
        frows = np.where(np.count_nonzero(self._board, axis=0) == self._width)
        frows = frows[0]
        if len(frows) > 0:
            # Remove the rows and sum score
            # TODO: Count the scores correctly
            self._score += len(frows)
            self._rows += len(frows)
            self._board[:, frows] = 0

            # Gravity - move all down to fill
            # Get all rows with non-zero elements
            nzrows = np.unique(np.nonzero(self._board)[1])
            nind = np.linspace(self._height - len(nzrows), self._height - 1,
                               len(nzrows), dtype=int)
            # Clean and move
            temp = self._board[:, nzrows]
            self._board *= 0
            self._board[:, nind] = temp
