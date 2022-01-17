import numpy as np
import tetromino
import random


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
        self._score = 0
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

    def spawn_tetromino(self):
        """TODO: Docstring for add_tetromino.

        :f: TODO
        :returns: TODO

        """
        self._active = self._next_tetromino()
        # Initial placement is middle justified by tetromino height
        self._active.move(transl=[int(self._width/2),
                                  -min(self._active.get_blocks()[:, 1])])

    def game_tick(self):
        """TODO: Docstring for move_active.

        :direction: TODO
        :returns: TODO

        """
        coll_id = self.move_active(transl=[0, 1])

        return coll_id

    def move_active(self, transl=[0, 0], rotdeg=0):
        """
        """
        coll_id = self.move_collision(transl=transl, rotdeg=rotdeg)
        if coll_id == 0:
            self._active.move(transl=transl, rotdeg=rotdeg)

        return coll_id

    def move_collision(self, transl=[0, 0], rotdeg=0):
        """Checks that a move does not lead to collision.

        :returns: 1 if edge collision, 2 if block collision, 0 if none
        """
        blocks = self._active.get_blocks(transl=transl, rotdeg=rotdeg)
        # If going outside of game board
        if blocks[:, 0].min() < 0 or blocks[:, 0].max() >= self._width:
            return 1
        # Hits end or another block
        elif max(blocks[:, 1]) == self._height \
                or np.any(self._board[blocks[:, 0], blocks[:, 1]]):
            return 2

        return 0

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
