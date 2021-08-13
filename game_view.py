import tkinter as tk

class View:
    BACKGROUND_COLOR = '#92877d'
    CELL_WIDTH=10
    CELL_HEIGHT=5
    CELL_PADDING=10
    UP_KEYS = ('w', 'W', 'Up')
    LEFT_KEYS = ('a', 'A', 'Left')
    DOWN_KEYS = ('s', 'S', 'Down')
    RIGHT_KEYS = ('d', 'D', 'Right')
    SPACE_KEYS = ('space')
    FONT = ('Verdana', 24, 'bold')

    CELL_BACKGROUND_COLOR_DICT = {
        '0': '#9e948a',
        '2': '#eee4da',
        '4': '#ede0c8',
        '8': '#f2b179',
        '16': '#f59563',
        '32': '#f67c5f',
        '64': '#f65e3b',
        '128': '#edcf72',
        '256': '#edcc61',
        '512': '#edc850',
        '1024': '#edc53f',
        '2048': '#edc22e',
        'beyond': '#3c3a32'
    }

    CELL_COLOR_DICT = {
        '2': '#776e65',
        '4': '#776e65',
        '8': '#f9f6f2',
        '16': '#f9f6f2',
        '32': '#f9f6f2',
        '64': '#f9f6f2',
        '128': '#f9f6f2',
        '256': '#f9f6f2',
        '512': '#f9f6f2',
        '1024': '#f9f6f2',
        '2048': '#f9f6f2',
        'beyond': '#f9f6f2'
    }

class BitboardView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('2048')
        self.grid_labels = []
        self.init_grid()

    def init_grid(self):
        self.background = tk.Frame(self.root, bg=View.BACKGROUND_COLOR)
        for i in range(4):
            row_labels = []
            for j in range(4):
                label = tk.Label(self.background, text='', justify=tk.CENTER, width=View.CELL_WIDTH, height=View.CELL_HEIGHT, font=View.FONT, bg=View.CELL_BACKGROUND_COLOR_DICT['0'])
                label.grid(row=i, column=j, padx=View.CELL_PADDING, pady=View.CELL_PADDING)
                row_labels.append(label)
            self.grid_labels.append(row_labels)
        self.background.grid()

    def render(self, board):
        bitboard = int(board)
        for i in range(4):
            for j in range(4):
                shift = 4 * (3-i) + (3-j)
                num = (bitboard >> (shift*4)) & 0xF
                if num != 0:
                    num = 2**num
                if num == 0:
                    bg_color = View.CELL_BACKGROUND_COLOR_DICT['0']
                    self.grid_labels[i][j].configure(text= '', bg=bg_color)
                else:
                    if num > 2048:
                        bg_color = View.CELL_BACKGROUND_COLOR_DICT['beyond']
                        fg_color = View.CELL_COLOR_DICT['beyond']
                    else:
                        bg_color = View.CELL_BACKGROUND_COLOR_DICT[str(num)]
                        fg_color = View.CELL_COLOR_DICT[str(num)]
                    self.grid_labels[i][j].configure(text=str(num), bg=bg_color, fg=fg_color)
