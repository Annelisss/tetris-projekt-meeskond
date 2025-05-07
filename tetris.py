import PySimpleGUI as sg
import random
import time
import pygame
import threading

# Board configuration
BOARD_WIDTH = 12
BOARD_HEIGHT = 20
NORMAL_TICK = 500  # Normal fall speed in milliseconds
FAST_TICK = 0.005 # Fast fall speed in milliseconds

# Tetromino shapes
TETROMINOES = {
    'O': [[1, 1], [1, 1]],
    'I': [[1, 1, 1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}

# Path to your MP3 file
MUSIC_PATH = "tetris-theme-korobeiniki.mp3"  # Ensure this file exists

def play_music():
    """Play Tetris theme music in a loop."""
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Music error:", e)

def create_board():
    """Create an empty game board."""
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def draw_board(window, board, score):
    """Update GUI to reflect current board state and score."""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            color = 'black' if board[y][x] == 0 else 'blue'
            window[(x, y)].update(button_color=('white', color))
    window["score_text"].update(f"Score: {score}")

def place_shape(board, shape, pos, value):
    """Place or remove shape on board."""
    sx, sy = pos
    for dy, row in enumerate(shape):
        for dx, val in enumerate(row):
            if val and 0 <= sy + dy < BOARD_HEIGHT and 0 <= sx + dx < BOARD_WIDTH:
                board[sy + dy][sx + dx] = value

def is_valid(board, shape, pos):
    """Check if shape can legally be placed."""
    sx, sy = pos
    for dy, row in enumerate(shape):
        for dx, val in enumerate(row):
            if val:
                x = sx + dx
                y = sy + dy
                if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                    return False
                if y >= 0 and board[y][x] == 1:
                    return False
    return True

def clear_lines(board):
    """Clear full rows and shift everything down."""
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines_cleared = BOARD_HEIGHT - len(new_board)
    while len(new_board) < BOARD_HEIGHT:
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, lines_cleared

def rotate(shape):
    """Rotate shape 90° clockwise."""
    return [list(row)[::-1] for row in zip(*shape)]

def run_tetris():
    """Main Tetris game loop."""
    # --- Start Game Popup ---
    start_layout = [[sg.Text("Click the Start button to play Tetris!")], [sg.Button("Start")]]
    start_window = sg.Window("Start Game", start_layout, finalize=True)
    start_event, _ = start_window.read()
    start_window.close()

    if start_event != "Start":
        return  # Exit if the user doesn't press Start

    # --- Initialize Game ---
    threading.Thread(target=play_music, daemon=True).start()
    board = create_board()
    layout = [
        [sg.Button('', size=(2, 1), pad=(0, 0), key=(x, y)) for x in range(BOARD_WIDTH)]
        for y in range(BOARD_HEIGHT)
    ]
    layout.append([sg.Text("Score: 0", key="score_text"), sg.Button('Exit')])
    window = sg.Window('Tetris', layout, return_keyboard_events=True, finalize=True, use_default_focus=False)

    shape = random.choice(list(TETROMINOES.values()))
    pos = [BOARD_WIDTH // 2 - len(shape[0]) // 2, 0]
    score = 0
    last_tick = time.time()
    fast_mode = False  # Add a variable to track fast mode
    game_over = False

    while not game_over:
        event, _ = window.read(timeout=10)
        now = time.time()

        # Handle events for controls
        if event == 'Left:37':
            place_shape(board, shape, pos, 0)
            new_pos = [pos[0] - 1, pos[1]]
            if is_valid(board, shape, new_pos):
                pos = new_pos
            place_shape(board, shape, pos, 1)
            draw_board(window, board, score)
        elif event == 'Right:39':
            place_shape(board, shape, pos, 0)
            new_pos = [pos[0] + 1, pos[1]]
            if is_valid(board, shape, new_pos):
                pos = new_pos
            place_shape(board, shape, pos, 1)
            draw_board(window, board, score)
        elif event == 'Up:38':
            place_shape(board, shape, pos, 0)
            rotated = rotate(shape)
            if is_valid(board, rotated, pos):
                shape = rotated
            place_shape(board, shape, pos, 1)
            draw_board(window, board, score)
        elif event == 'Down:40':
            fast_mode = True  # Enable fast mode when down arrow is pressed
        elif event not in ('Down:40',):
            fast_mode = False # Disable when other keys are pressed

        current_tick = FAST_TICK if fast_mode else NORMAL_TICK #set the speed

        # Auto-drop tick
        if now - last_tick > current_tick / 1000:
            place_shape(board, shape, pos, 0)
            new_pos = [pos[0], pos[1] + 1]
            if is_valid(board, shape, new_pos):
                pos = new_pos
            else:
                place_shape(board, shape, pos, 1)
                board, cleared = clear_lines(board)
                score += cleared * 100
                shape = random.choice(list(TETROMINOES.values()))
                pos = [BOARD_WIDTH // 2 - len(shape[0]) // 2, 0]
                if not is_valid(board, shape, pos):
                    pygame.mixer.music.stop()
                    sg.popup("Game Over", title="Tetris")
                    game_over = True
                    break
            place_shape(board, shape, pos, 1)
            draw_board(window, board, score)
            last_tick = now

        if event in (sg.WIN_CLOSED, 'Exit'):
            pygame.mixer.music.stop()
            game_over = True
            break

    window.close()


# Run the game
if __name__ == '__main__':
    run_tetris()