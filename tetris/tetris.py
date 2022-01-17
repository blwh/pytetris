import numpy as np
import tetromino
import time
import random


class Tetris(object):

    """Docstring for Tetris. """

    def __init__(self, width, height, queue_len=5):
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

    def _get_from_queue(self):
        """Gets Tetromino from queue and refills it up to queue_len.

        If the queue is empty, generate a random Tetromino.
        """

        if len(self._queue) == 0:
            type_ = random.choice(list(tetromino.Tetrominoes))
            next_tetromino = tetromino.Tetromino(type_)
        else:
            next_tetromino = self._queue.pop(0)

        for _ in range(self._queue_len - len(self._queue)):
            type_ = random.choice(list(tetromino.Tetrominoes))
            self._queue.append(tetromino.Tetromino(type_))

        return next_tetromino

    def print_board(self):
        """TODO: Docstring for print_board.
        :returns: TODO

        """
        for i in range(self._height):
            row = ''
            for j in range(self._width):
                row += str(self._board[j, i])
            print(row)
        print('')

    def tetromino_from_queue(self, pos=0):

        grid = self._queue[pos].blocks
        val = self._queue[pos]._type.value
        for x, y in grid:
            yield x, y, val

    def filled_board_grid(self):
        """Iterator to return the position and vals of filled grid points.

        :returns: Iterator with pos x, pos y and value
        """

        for i in range(self._height):
            for j in range(self._width):
                if self._board[j, i] != 0:
                    yield j, i, self._board[j, i]

    def add_tetromino(self):
        """TODO: Docstring for add_tetromino.

        :f: TODO
        :returns: TODO

        """

        self._active = self._get_from_queue()
        # Randomly rotate the new tetromino
        self._active.rotate(np.random.choice([0, 90, 180, 270]))
        # Initial placement is middle justified by tetromino height
        self._active.move(direction=[int(self._width/2),
                                     -min(self._active.blocks[:, 1])])

        # Placement not possible -> game ends
        if np.any(self._board[self._active.blocks[:, 0],
                              self._active.blocks[:, 1]]):
            self.add_active()
            return False

        self.add_active()

        return True

    def game_tick(self, direction=[0, 1]):
        """TODO: Docstring for move_active.

        :direction: TODO
        :returns: TODO

        """

        self.remove_active()
        ret_val = True

        # If the active reached the end
        if max(self._active.blocks[:, 1]) == self._height - 1:
            ret_val = False
        else:
            self._active.move(direction=direction)
            # Checks if next step is viable
            if np.any(self._board[self._active.blocks[:, 0],
                                  self._active.blocks[:, 1]]):
                # In a horrible way move the piece back
                self._active.move(direction=[-a for a in direction])
                ret_val = False

        self.add_active()

        return ret_val

    def move_active_left(self):

        self.remove_active()
        self._active.move([-1, 0])
        if not self.check_possible_move():
            self._active.move([1, 0])
        self.add_active()

    def move_active_right(self):

        self.remove_active()
        self._active.move([1, 0])
        if not self.check_possible_move():
            self._active.move([-1, 0])
        self.add_active()

    def rotate_active(self):

        self.remove_active()
        self._active.rotate(90)
        if not self.check_possible_move():
            self._active.rotate(-90)
        self.add_active()

    def check_possible_move(self):
        """Checks that a move is possible.

        :returns: 
        """
        # If going outside of game board
        if self._active.blocks[:, 0].min() < 0 or \
           self._active.blocks[:, 0].max() >= self._width:
            return False
        if np.any(self._board[self._active.blocks[:, 0],
                              self._active.blocks[:, 1]]):
            return False

        return True

    def add_active(self):
        """Sets the active blocks on the board to the tetrominoe value.

        :returns: None
        """
        self._board[self._active.blocks[:, 0], self._active.blocks[:, 1]] = \
                self._active._type.value

    def remove_active(self):
        """Sets the active blocks on the board to zero.

        :returns: None
        """
        self._board[self._active.blocks[:, 0], self._active.blocks[:, 1]] = 0

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


if __name__ == "__main__":

    tetris = Tetris(14, 30)
    tetris.print_board()
    tetris.add_tetromino()

    while True:
        # tetris.add_active()
        tetris.print_board()
        time.sleep(0.2)
        # tetris.remove_active()
        if not tetris.game_tick():
            # tetris.add_active()
            tetris.check_rows()
            if not tetris.add_tetromino():
                break

    print('You failed')
