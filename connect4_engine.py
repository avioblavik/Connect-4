import pygame
import numpy as np
import random
import sys
import math

# Constants
ROWS = 6
COLS = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
WIDTH = COLS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Connect 4")

# Font for winner message
FONT = pygame.font.SysFont("monospace", 75)
SMALL_FONT = pygame.font.SysFont("monospace", 50)

def create_board():
    """Creates an empty board."""
    return np.zeros((ROWS, COLS), dtype=int)

def draw_board(board):
    """Draws the Connect 4 board on the screen."""
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (c * SQUARESIZE + SQUARESIZE // 2, r * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2), RADIUS)

    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (c * SQUARESIZE + SQUARESIZE // 2, HEIGHT - (r * SQUARESIZE + SQUARESIZE // 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, YELLOW, (c * SQUARESIZE + SQUARESIZE // 2, HEIGHT - (r * SQUARESIZE + SQUARESIZE // 2)), RADIUS)

    pygame.display.update()

def is_valid_location(board, col):
    """Checks if a column can accept another piece."""
    return board[ROWS - 1][col] == 0

def get_next_open_row(board, col):
    """Finds the next available row in the specified column."""
    for r in range(ROWS):
        if board[r][col] == 0:
            return r

def drop_piece(board, row, col, piece):
    """Places a piece in the board at the specified location."""
    board[row][col] = piece

def winning_move(board, piece):
    """Checks if the given piece has four in a row."""
    # Check horizontal locations
    for c in range(COLS - 3):
        for r in range(ROWS):
            if (board[r][c] == piece and board[r][c + 1] == piece and
                board[r][c + 2] == piece and board[r][c + 3] == piece):
                return True

    # Check vertical locations
    for c in range(COLS):
        for r in range(ROWS - 3):
            if (board[r][c] == piece and board[r + 1][c] == piece and
                board[r + 2][c] == piece and board[r + 3][c] == piece):
                return True

    # Check positively sloped diagonals
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if (board[r][c] == piece and board[r + 1][c + 1] == piece and
                board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece):
                return True

    # Check negatively sloped diagonals
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if (board[r][c] == piece and board[r - 1][c + 1] == piece and
                board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece):
                return True

    return False

def get_valid_locations(board):
    """Returns a list of valid columns."""
    return [col for col in range(COLS) if is_valid_location(board, col)]

def score_position(board, piece):
    """Evaluates the score of a board position for a given player."""
    score = 0

    # Center column preference
    center_array = [int(i) for i in list(board[:, COLS // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Horizontal score
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # Vertical score
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r + 4]
            score += evaluate_window(window, piece)

    # Positive diagonal score
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative diagonal score
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def evaluate_window(window, piece):
    """Evaluates a 4-element window."""
    score = 0
    opp_piece = 1 if piece == 2 else 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score

def is_terminal_node(board):
    """Checks if the game is over."""
    return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    """Minimax algorithm with Alpha-Beta pruning."""
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 100000000000000)
            elif winning_move(board, 1):
                return (None, -10000000000000)
            else:  # No more valid moves
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, 2))

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 2)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:  # Minimizing player
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 1)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

def main():
    board = create_board()
    game_over = False
    turn = 0

    draw_board(board)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if turn == 0:  # Player 1
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                    posx = event.pos[0]
                    if turn == 0:
                        pygame.draw.circle(screen, RED, (posx, SQUARESIZE // 2), RADIUS)
                    else:
                        pygame.draw.circle(screen, YELLOW, (posx, SQUARESIZE // 2), RADIUS)
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))

                    posx = event.pos[0]
                    col = posx // SQUARESIZE

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, turn + 1)

                        if winning_move(board, turn + 1):
                            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                            label = FONT.render(f"Human wins!", True, RED )
                            screen.blit(label, (40, 10))
                            game_over = True

                        draw_board(board)

                        turn = 1
                        


            elif turn == 1:  # AI Player 2
                pygame.time.wait(1000)  # Pause for a moment for AI's turn
                col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 2)

                    if winning_move(board, 2):
                        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                        label = FONT.render("AI wins!", True, YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    draw_board(board)
                    turn = 0

        if game_over:
            pygame.time.wait(3000)
            sys.exit()

if __name__ == "__main__":
    main()
