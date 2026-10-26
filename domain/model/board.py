class Board():
    def __init__(self, board = None):
        self.board = board or [[" " for _ in range(3)] for _ in range(3)]

    def get_cell(self, row, col):
        return self.board[row][col]

    def set_cell(self, row, col, value):
        self.board[row][col] = value

    def is_full(self):
        return all(c != " " for row in self.board for c in row)

    def clone(self):
        return Board([row[:] for row in self.board])