import tkinter as tk
import random
import tkinter.messagebox
import pygame

# Mängulaua mõõtmed ja ruudu suurus pikslites
BOARD_WIDTH = 10     # veergude arv
BOARD_HEIGHT = 20    # ridade arv
CELL_SIZE = 30       # ühe ruudu suurus

# Aja viivitus millisekundites (tavaline ja kiirendatud langus)
DELAY = 500
FAST_DELAY = 0.05

# Tetromino kujundite definitsioonid (2D massiivid)
TETROMINOES = {
    'O': [[1, 1], [1, 1]],
    'I': [[1, 1, 1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}

# Värvide määramine: 0 = tühi (must), 1 = täidetud (sinine)
COLORS = {
    0: "black",
    1: "blue"
}

class TetrisGame:
    def __init__(self):
        # Loo mängu põhiaken
        self.root = tk.Tk()
        self.root.title("Tetris")

        # Arvuta ja loo mänguväli (canvas)
        canvas_width = BOARD_WIDTH * CELL_SIZE + 4
        canvas_height = BOARD_HEIGHT * CELL_SIZE + 4
        self.canvas = tk.Canvas(self.root, width=canvas_width, height=canvas_height, bg="black")
        self.canvas.pack()

        # Skoori ja taseme sildid (labelid)
        self.score_label = tk.Label(self.root, text="Score: 0", font=("Arial", 14), bg="black", fg="white")
        self.score_label.pack()
        self.level_label = tk.Label(self.root, text="Level: 1", font=("Arial", 14), bg="black", fg="white")
        self.level_label.pack()

        # Start-nupp mängu alustamiseks
        self.start_button = tk.Button(
            self.root,
            text="START",
            font=("Arial", 18, "bold"),
            width=10,
            height=2,
            bg="#3399FF",
            fg="white",
            activebackground="#66CCFF",
            relief="raised",
            bd=4,
            command=self.start_game
        )
        self.start_button.place(relx=0.5, rely=0.7, anchor="center")

        # Joonista pikselgraafikas TETRIS logo
        self.draw_tetris_logo()

        # Initsialiseeri muusika pygame abil
        pygame.mixer.init()
        pygame.mixer.music.load("tetris-theme-korobeiniki.mp3")
        pygame.mixer.music.set_volume(0.3)

        # Käivita GUI sündmuste tsükkel
        self.root.mainloop()

    def draw_tetris_logo(self):
        # Joonista suur pikselstiilis "TETRIS" logo canvas'ile
        pixel_size = 10
        offset_y = BOARD_HEIGHT * CELL_SIZE // 4  # vertikaalne tsentreerimine

        # Tähtede mustrid
        letters = {
            'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  "],
            'E': ["#####", "#    ", "#####", "#    ", "#####"],
            'R': ["#### ", "#   #", "#### ", "#  # ", "#   #"],
            'I': [" ### ", "  #  ", "  #  ", "  #  ", " ### "],
            'S': [" ####", "#    ", " ### ", "    #", "#### "],
        }

        word = "TETRIS"
        total_width = len(word) * 5
        canvas_width = self.canvas.winfo_reqwidth()
        offset_x = (canvas_width - total_width * pixel_size) // 2

        # Joonista iga täht
        for idx, char in enumerate(word):
            pattern = letters.get(char)
            if not pattern:
                continue
            for row_idx, row in enumerate(pattern):
                for col_idx, val in enumerate(row):
                    if val == "#":
                        x0 = offset_x + (idx * 5 + col_idx) * pixel_size
                        y0 = offset_y + row_idx * pixel_size
                        x1 = x0 + pixel_size
                        y1 = y0 + pixel_size
                        self.canvas.create_rectangle(x0, y0, x1, y1, fill="#33B5FF", outline="black")

    def start_game(self):
        # Eemalda avaleht ja alusta mängu
        self.start_button.destroy()
        self.canvas.delete("all")
        pygame.mixer.music.play(-1)  # taasesita muusikat lõputult
        self.restart()

    def restart(self):
        # Taasta mängu algseis
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.shape = self.new_shape()
        self.pos = [BOARD_WIDTH // 2 - len(self.shape[0]) // 2, 0]
        self.score = 0
        self.level = 1
        self.delay = DELAY
        self.running = True
        self.fast = False

        # Värskenda kasutajaliidest
        self.score_label.config(text="Score: 0")
        self.level_label.config(text="Level: 1")
        self.canvas.delete("gameover")

        # Seosta klahvinupud ja käivita mängutsükkel
        self.root.bind("<Key>", self.key_press)
        self.game_loop()

    def new_shape(self):
        # Tagasta suvaline tetromino kujund
        return random.choice(list(TETROMINOES.values()))

    def draw(self):
        # Joonista mängulaud ja hetkel langev kujund
        if not self.running:
            return
        self.canvas.delete("all")

        # Joonista olemasolevad kivid
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                self.draw_cell(x, y, self.board[y][x])

        # Joonista aktiivne kujund
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(self.pos[0] + x, self.pos[1] + y, 1)

        # Joonista piir
        self.canvas.create_rectangle(
            1, 1,
            BOARD_WIDTH * CELL_SIZE + 2,
            BOARD_HEIGHT * CELL_SIZE + 2,
            outline="white",
            width=2
        )

    def draw_cell(self, x, y, value):
        # Joonista üks ruut positsioonil (x, y) vastava värviga
        color = COLORS.get(value, "gray")
        x0 = x * CELL_SIZE + 2
        y0 = y * CELL_SIZE + 2
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="gray")

    def key_press(self, event):
        # Töötle klaviatuurisisendeid
        if not self.running:
            return
        key = event.keysym.lower()
        if key == 'a':  # vasakule
            self.move(-1, 0)
        elif key == 'd':  # paremale
            self.move(1, 0)
        elif key == 's':  # alla
            self.move(0, 1)
        elif key == 'w':  # pööra
            self.rotate()
        elif key == 'space':  # kiirlaskumine
            self.fast = True

    def game_loop(self):
        # Mängutsükkel, mis kutsub end uuesti pärast viivitust
        if not self.running:
            return
        self.update()
        self.draw()
        delay = FAST_DELAY if self.fast else self.delay
        self.fast = False
        self.root.after(delay, self.game_loop)

    def update(self):
        # Proovi kujundit liigutada või fikseeri see
        if self.valid_move(0, 1):
            self.pos[1] += 1
        else:
            self.merge()
            self.clear_lines()
            next_shape = self.new_shape()
            next_pos = [BOARD_WIDTH // 2 - len(next_shape[0]) // 2, 0]
            if not self.valid_move_at(next_shape, next_pos):
                self.game_over()
            else:
                self.shape = next_shape
                self.pos = next_pos

    def move(self, dx, dy):
        # Liiguta kujundit suunas (dx, dy)
        if self.valid_move(dx, dy):
            self.pos[0] += dx
            self.pos[1] += dy

    def rotate(self):
        # Pööra kujundit päripäeva
        rotated = [list(row)[::-1] for row in zip(*self.shape)]
        old_shape = self.shape
        self.shape = rotated
        if not self.valid_move(0, 0):
            self.shape = old_shape  # kui liigutus pole lubatud, taasta

    def valid_move(self, dx, dy):
        # Kontrolli, kas liigutus (dx, dy) on kehtiv
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = self.pos[0] + x + dx
                    ny = self.pos[1] + y + dy
                    if nx < 0 or nx >= BOARD_WIDTH or ny < 0 or ny >= BOARD_HEIGHT:
                        return False
                    if self.board[ny][nx]:
                        return False
        return True

    def valid_move_at(self, shape, pos):
        # Kontrolli, kas kujundit saab paigutada antud asukohta
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = pos[0] + x
                    ny = pos[1] + y
                    if nx < 0 or nx >= BOARD_WIDTH or ny < 0 or ny >= BOARD_HEIGHT:
                        return False
                    if self.board[ny][nx]:
                        return False
        return True

    def merge(self):
        # Lisa kujund mängulauale
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.board[self.pos[1] + y][self.pos[0] + x] = 1

    def clear_lines(self):
        # Kustuta täidetud read ja uuenda skoori
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        cleared = BOARD_HEIGHT - len(new_board)
        for _ in range(cleared):
            new_board.insert(0, [0] * BOARD_WIDTH)
        self.board = new_board
        self.score += cleared * 100
        self.score_label.config(text=f"Score: {self.score}")
        self.adjust_speed()

    def adjust_speed(self):
        # Kohanda kiirust vastavalt tasemele
        new_level = self.score // 500 + 1
        new_delay = max(100, DELAY - (new_level - 1) * 50)
        if new_level != self.level:
            self.level = new_level
            self.level_label.config(text=f"Level: {self.level}")
        if new_delay != self.delay:
            self.delay = new_delay

    def draw_pixel_text(self, text, y_offset=100, color="#33B5FF"):
        # Kuvab ekraanile suure pikseltekstina sõnumi (nt "GAME OVER")
        pixel_size = 10
        spacing = 1
        line_height = 6 * pixel_size

        letters = {
            'A': [" ### ", "#   #", "#####", "#   #", "#   #"],
            'E': ["#####", "#    ", "#####", "#    ", "#####"],
            'G': [" ### ", "#    ", "#  ##", "#   #", " ### "],
            'M': ["#   #", "## ##", "# # #", "#   #", "#   #"],
            'O': [" ### ", "#   #", "#   #", "#   #", " ### "],
            'V': ["#   #", "#   #", "#   #", " # # ", "  #  "],
            'R': ["#### ", "#   #", "#### ", "#  # ", "#   #"],
            ' ': ["     ", "     ", "     ", "     ", "     "]
        }

        lines = text.upper().split('\n')
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        total_height = len(lines) * line_height
        base_y = (canvas_height - total_height) // 2 + y_offset

        for line_idx, line in enumerate(lines):
            total_width = len(line) * 6 * pixel_size
            x_offset = (canvas_width - total_width) // 2
            y_offset_line = base_y + line_idx * line_height

            for idx, char in enumerate(line):
                pattern = letters.get(char, letters[' '])
                for row_idx, row in enumerate(pattern):
                    for col_idx, val in enumerate(row):
                        if val == "#":
                            x0 = x_offset + (idx * 6 + col_idx) * pixel_size
                            y0 = y_offset_line + row_idx * pixel_size
                            x1 = x0 + pixel_size
                            y1 = y0 + pixel_size
                            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black", tags="gameover")

    def game_over(self):
        # Peata mäng ja kuva mängu lõpp
        self.running = False
        self.draw()
        self.draw_pixel_text("GAME\nOVER", y_offset=-20)
        self.root.after(1000, self.show_restart_prompt)

    def show_restart_prompt(self):
        # Küsi kasutajalt, kas ta tahab uuesti mängida
        response = tk.messagebox.askquestion("Game Over", f"Your score: {self.score}\nPlay again?")
        if response == "yes":
            self.restart()
        else:
            self.root.destroy()

# Programmi käivitamine
if __name__ == "__main__":
    TetrisGame()
