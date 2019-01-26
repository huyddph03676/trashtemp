
# class Add(int):
#     def __call__(self, number):
#         return Add(self + number)

SudokuBoard = [[0,0,4,9,6,2,3,0,0],
               [0,6,0,1,0,0,4,0,0],
               [8,2,0,3,7,0,0,0,6],
               [0,0,1,4,0,6,0,2,0],
               [0,0,2,7,5,0,0,0,0],
               [0,9,3,2,0,0,7,0,4],
               [2,7,0,0,3,0,9,4,0],
               [1,0,0,0,0,0,2,7,5],
               [9,0,0,8,2,0,0,0,1]]


def number_unasigned(board):
    number_unasign = 0
    for i in range(9):
        for j in range(9):
            # Checking empty cell and get index
            if board[i][j] == 0:
                row = i
                col = j
                number_unasign = 1
                return [row, col, number_unasign]
    return [-1, -1, number_unasign]

def is_safe(n,r,c,board):
    # Checking Row
    for i in range(9):
        if board[r][i] == n:
            return False
    # Checking Column
    for i in range(9):
        if board[i][c] == n:
            return False
    # Checking 3 x 3
    c_start = (c // 3) * 3
    r_start = (r // 3) * 3
    for x in range(r_start, r_start + 3):
        for y in range(c_start, c_start + 3):
            if board[x][y] == n:
                return False
    return True

def sudoku_Solve(board):
    a = number_unasigned(board)
    if a[2] == 0:
        return True
    row = a[0]
    col = a[1]
    for i in range(1,10):
        if is_safe(i,row,col,board):
            board[row][col] = i
            if sudoku_Solve(board):
                return True
        board[row][col] = 0
    return False






