# PyQt5 imports
from PyQt5.QtCore import QTimer, QBasicTimer, Qt, pyqtSignal
from PyQt5.QtWidgets import (
        QMainWindow, QApplication, QFrame, QWidget, QLabel
        )
from PyQt5.QtGui import QPainter, QColor

# Additional imports
import sys

# Local imports
from tetris import Tetris

# Dict mapping tetromino value to color
color_from_tetromino = {1: '#047af6', 2: '#dcaa15', 3: '#f1c74c', 4: '#afeeee',
                        5: '#7401df', 6: '#32fa00', 7: '#f40073'}


# creating game window
class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()

        # setting title to the window
        self.setWindowTitle('Tetris')

        # The game dimensions
        self.tetrisdims = [10, 30]
        self.scale_factor = 20

        # Set the window size
        self.resize(250, 470)

        # Initialize the UI
        self.init_ui()

        # showing the main window
        self.show()

    def init_ui(self):

        # The main widget
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Tetris game
        self.tetris = Tetris(self.tetrisdims[0], self.tetrisdims[1])

        # Create the game board
        self.tetrisboard = TetrisBoard(wid, self.tetris)
        self.tetrisboard.setStyleSheet("background-color: white;" +
                                       "border: 3px solid black;")
        self.tetrisboard.setFocusPolicy(Qt.StrongFocus)
        self.tetrisboard.setGeometry(10, 10,
                                     self.scale_factor*self.tetrisdims[0],
                                     self.scale_factor*self.tetrisdims[1])

        # TODO: Fix the score widget
        self.score = QLabel('Score: 0', self)
        self.tetrisboard.score_label[str].connect(self.score.setText)
        self.score.move(20 + self.scale_factor*self.tetrisdims[0], 20)

        # Widget to show coming tetrominos
        self.tetrominoqueue = TetrominoQueue(self, self.tetris,
                                             [5, 1*5])
        self.tetrominoqueue.setStyleSheet("background-color: white;" +
                                          "border: 3px solid black;")
        self.tetrisboard.tetrominoqueue.connect(self.tetrominoqueue.update)
        self.tetrominoqueue.setGeometry(
                20 + self.scale_factor*self.tetrisdims[0], 60,
                self.scale_factor*5, self.scale_factor*(1*5))

        # Initialize the game
        self.tetrisboard.start()
        self.tetrominoqueue.update()


class TetrominoQueue(QFrame):

    # constructor
    def __init__(self, parent, tetris, dims):
        super(TetrominoQueue, self).__init__(parent)

        self._tetris = tetris
        self.dims = dims

    def square_width(self):
        return int(self.contentsRect().width()/self.dims[0])

    def square_height(self):
        return int(self.contentsRect().height()/self.dims[1])

    def paintEvent(self, event):

        # Painter object
        painter = QPainter(self)

        # The area inside the widget's margins
        rect = self.contentsRect()

        # board top
        boardtop = rect.bottom() - self.dims[1] * self.square_height()

        # board top
        boardtop = rect.top()
        for pos in range(1):
            for x, y, val in self._tetris.tetromino_blocks(active=False, pos=pos):
                color = QColor(color_from_tetromino[val])
                # painting rectangle
                # TODO: This is a fucking mess, fix
                painter.fillRect(
                        rect.left() + (x+2)*self.square_width(),
                        boardtop + (y+3)*self.square_height(),
                        self.square_width() - 2,
                        self.square_height() - 2, color)


class TetrisBoard(QFrame):

    score_label = pyqtSignal(str)
    tetrominoqueue = pyqtSignal()

    # Lock time (ms)
    LOCKTIME = 500

    # constructor
    def __init__(self, parent, tetris):
        super(TetrisBoard, self).__init__(parent)

        # Store the tetris instance
        self.tetris = tetris
        # and get the dimensions
        self.gamedims = [self.tetris._width, self.tetris._height]
        # msec per tick
        self.tick_interval = 50

        # TODO: This might be a bit inefficient
        self.nskips = 3  # number of skipped ticks if not soft-dropping
        self.skips = 0

        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.game_tick)
        self.lock_timer = QTimer(self)
        self.lock_timer.timeout.connect(self.lock_event)

        self.lock = False  # If lock timer is initialized
        self.soft_drop = False  # If soft dropping

    def square_width(self):
        return int(self.contentsRect().width()/self.gamedims[0])

    def square_height(self):
        return int(self.contentsRect().height()/self.gamedims[1])

    def start(self):
        # starting timer
        self.game_timer.start(self.tick_interval)
        # Add the first tetromino
        self.tetris.spawn_tetromino()

    def lock_event(self):

        self.tetris.lock_active()  # Lock the piece to the board
        self.tetris.check_rows()  # Check which rows to remove
        # Signal to update next and scores
        self.tetrominoqueue.emit()
        self.score_label.emit('Score: ' + str(self.tetris._score))
        # Spawn a new piece and stop the lock timer
        self.tetris.spawn_tetromino()
        self.lock_timer.stop()
        self.lock = False
        self.soft_drop = False

        self.update()

    def game_tick(self):

        if self.skips == self.nskips - 1 or self.soft_drop:
            coll_id = self.tetris.game_tick()
            # Checks if the lock event should initialize
            if coll_id == 2:
                if not self.lock:
                    self.lock_timer.start(TetrisBoard.LOCKTIME)
                    self.lock = True
            self.skips = 0
            self.update()
        else:
            self.skips += 1

    def paintEvent(self, event):

        # Painter object
        painter = QPainter(self)
        # The area inside the widget's margins
        rect = self.contentsRect()
        # board top
        boardtop = rect.bottom() - self.gamedims[1] * self.square_height()

        # Draw the board
        for x, y, val in self.tetris.board_blocks():
            self.draw_square(painter, rect.left() + x * self.square_width(),
                             boardtop + y * self.square_height(), val)

        # Draw the active Tetromino
        for x, y, val in self.tetris.tetromino_blocks():
            self.draw_square(painter, rect.left() + x * self.square_width(),
                             boardtop + y * self.square_height(), val)

    def draw_square(self, painter, x, y, val):

        # color
        color = QColor(color_from_tetromino[val])
        # painting rectangle
        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color)

    def keyPressEvent(self, event):

        # Get pressed key
        key = event.key()

        if key == Qt.Key_Left:
            self.tetris.move_active(transl=[-1, 0])
        elif key == Qt.Key_Right:
            self.tetris.move_active(transl=[1, 0])
        elif key == Qt.Key_Up:
            self.tetris.move_active(rotdeg=90)
        elif key == Qt.Key_Down and not event.isAutoRepeat():
            if not self.soft_drop:
                self.soft_drop = True

        self.update()

    def keyReleaseEvent(self, event):

        # Get pressed key
        key = event.key()

        if key == Qt.Key_Down and not event.isAutoRepeat():
            self.soft_drop = False

        self.update()


if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())
