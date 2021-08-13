import numpy as np
from  enum import Enum
import math

ROW_MASK = np.uint64(0xFFFF)
COL_MASK = np.uint64(0x000F000F000F000F)

class Action(Enum):
    Up = 0
    Left = 1
    Down = 2
    Right = 3

class BitboardModel:
    # Board represented as a 64 bit int, each nibble x representing a single cell 2^x
    def __init__(self, merge_lookup_left=None, merge_lookup_right=None, board=None):
        if board:
            self.board = board
        else:
            self.board = np.uint64(0)
        if not merge_lookup_right:
            self.merge_lookup_left, self.merge_lookup_right = create_merge_lookup_tables()
        else:
            self.merge_lookup_left = merge_lookup_left
            self.merge_lookup_right = merge_lookup_right
        
    def clone(self):
        return BitboardModel(self.merge_lookup_left, self.merge_lookup_right, self.board)
    
    def move(self, action):
        before = self.board
        moved = False

        if action == Action.Up:
            self.merge_up()
            moved = (before != self.board)

        if action == Action.Left:
            self.merge_left()
            moved = (before != self.board)

        if action == Action.Down:
            self.merge_down()
            moved = (before != self.board)

        if action == Action.Right:
            self.merge_right()
            moved = (before != self.board)
        return moved

    def merge_left(self):
        tmp = np.uint64(0)
        tmp ^= self.merge_lookup_left[(self.board >>  np.uint64(0)) & ROW_MASK] << np.uint64(0)
        tmp ^= self.merge_lookup_left[(self.board >> np.uint64(16)) & ROW_MASK] << np.uint64(16)
        tmp ^= self.merge_lookup_left[(self.board >> np.uint64(32)) & ROW_MASK] << np.uint64(32)
        tmp ^= self.merge_lookup_left[(self.board >> np.uint64(48)) & ROW_MASK] << np.uint64(48)
        self.board = tmp
    
    def merge_right(self):
        tmp = np.uint64(0)
        tmp ^= self.merge_lookup_right[(self.board >>  np.uint64(0)) & ROW_MASK] << np.uint64(0)
        tmp ^= self.merge_lookup_right[(self.board >> np.uint64(16)) & ROW_MASK] << np.uint64(16)
        tmp ^= self.merge_lookup_right[(self.board >> np.uint64(32)) & ROW_MASK] << np.uint64(32)
        tmp ^= self.merge_lookup_right[(self.board >> np.uint64(48)) & ROW_MASK] << np.uint64(48)
        self.board = tmp

    def merge_up(self):
        tmp = np.uint64(0)
        transposed = transpose_board(self.board)
        tmp ^= self.merge_lookup_left[(transposed >> np.uint64(0)) & ROW_MASK] << np.uint64(0)
        tmp ^= self.merge_lookup_left[(transposed >> np.uint64(16)) & ROW_MASK] << np.uint64(16)
        tmp ^= self.merge_lookup_left[(transposed >> np.uint64(32)) & ROW_MASK] << np.uint64(32)
        tmp ^= self.merge_lookup_left[(transposed >> np.uint64(48)) & ROW_MASK] << np.uint64(48)
        self.board = transpose_board(tmp)

    def merge_down(self):
        tmp = np.uint64(0)
        transposed = transpose_board(self.board)
        tmp ^= self.merge_lookup_right[(transposed >> np.uint64(0)) & ROW_MASK] << np.uint64(0)
        tmp ^= self.merge_lookup_right[(transposed >> np.uint64(16)) & ROW_MASK] << np.uint64(16)
        tmp ^= self.merge_lookup_right[(transposed >> np.uint64(32)) & ROW_MASK] << np.uint64(32)
        tmp ^= self.merge_lookup_right[(transposed >> np.uint64(48)) & ROW_MASK] << np.uint64(48)
        self.board = transpose_board(tmp)
    
    def add_random_tile(self):
        if np.random.rand() < 0.1:
            tile_value = 4
        else:
            tile_value = 2
        self.add_tile_at_random_pos(tile_value)

    def num_empty(self):
        empty_mask = get_empty_mask(self.board)
        return int(count_empty(empty_mask)/4)

    def add_tile_at_random_pos(self, x):
        n_empty = self.num_empty()
        if n_empty == 0:
            return
        index = np.random.randint(n_empty)
        self.add_tile_at_pos(x, index)

    def add_tile_at_pos(self, x, index):
        empty_mask = get_empty_mask(self.board)
        num = np.uint64(math.log2(x))
        mask = np.uint64(1)
        while(True):
            if(mask & empty_mask == np.uint64(0x1)):
                if index == 0:
                    self.board = self.board + num
                    return
                else:
                    index -= 1
            num = num << np.uint64(4)
            empty_mask = empty_mask >> np.uint64(4)

    def get_avail_moves(self):
        avail_moves= []
        for move in Action:
            clone = self.clone()
            if clone.move(move):
                avail_moves.append(move)
        return avail_moves

def create_merge_lookup_tables():
    merge_lookup_left = {}
    merge_lookup_right = {}
    for x in range(2**16):
        line = convert_to_row(x)
        row = np.uint64(x)
        merged_line = merge_grid_row_right(line)
        result = convert_to_16_bit(merged_line)
        rev_row = reverse_row(row)
        rev_result = reverse_row(result)
        merge_lookup_right[row] = result
        merge_lookup_left[rev_row] = rev_result
    return merge_lookup_left, merge_lookup_right

def reverse_row(row_num):
    a_1 = (row_num & np.uint64(0xF000)) >> np.uint64(12)
    a_2 = (row_num & np.uint64(0x0F00)) >> np.uint64(4)
    a_3 = (row_num & np.uint64(0x00F0)) << np.uint64(4)
    a_4 = (row_num & np.uint64(0x000F)) << np.uint64(12)
    return a_1 | a_2 | a_3 | a_4

def transpose_board(x):
    a1 = x & np.uint64(0xF0F00F0FF0F00F0F)
    a2 = x & np.uint64(0x0000F0F00000F0F0)
    a3 = x & np.uint64(0x0F0F00000F0F0000)
    a = a1 | (a2 << np.uint64(12)) | (a3 >> np.uint64(12))
    b1 = a & np.uint64(0xFF00FF0000FF00FF)
    b2 = a & np.uint64(0x00FF00FF00000000)
    b3 = a & np.uint64(0x00000000FF00FF00)
    return b1 | (b2 >> np.uint64(24)) | (b3 << np.uint64(24))

def convert_to_row(num):
    row = []
    for j in range(4):
        item = get_item(num, j)
        row.append(item)
    return row

def get_item(x, i):
    mask = 0xF << (4*(4-i-1))
    x = x & mask
    x = x >> (4*(4-i-1))
    if x == 0:
        return 0
    return 2**x

def convert_to_16_bit(row):
    for i in range(4):
        if row[i] != 0:
            row[i] = int(math.log2(row[i]))
        row[i] = row[i] << (4*(4-i-1))
    return np.uint64(sum(row))

def merge_grid_row_right(row):
    pos = 3
    num = 0
    for j in range(3, -1, -1):
        if row[j] == 0:
            continue
        if num == 0:
            num = row[j]
        elif num == row[j]:
            row[pos] = 2*num
            pos -= 1
            num = 0
        else:
            if row[pos] != num:
                row[pos] = num
            pos -= 1
            num = row[j]
    if num != 0:
        if row[pos] != num:
            row[pos] = num
        pos -= 1
    for j in range(pos+1):
        if row[j] != 0:
            row[j] = 0
    return row

def count_empty(x):
    m1  = np.uint64(0x5555555555555555)
    m2  = np.uint64(0x3333333333333333)
    m4  = np.uint64(0x0f0f0f0f0f0f0f0f)
    m8  = np.uint64(0x00ff00ff00ff00ff)
    m16 = np.uint64(0x0000ffff0000ffff)
    m32 = np.uint64(0x00000000ffffffff)
    x = (x & m1 ) + ((x >>  np.uint64(1)) & m1 )
    x = (x & m2 ) + ((x >>  np.uint64(2)) & m2 )
    x = (x & m4 ) + ((x >>  np.uint64(4)) & m4 )
    x = (x & m8 ) + ((x >>  np.uint64(8)) & m8 )
    x = (x & m16) + ((x >> np.uint64(16)) & m16)
    x = (x & m32) + ((x >> np.uint64(32)) & m32)
    return x

def get_even_empty_mask(x):
        x= ~x & np.uint64(0x0F0F0F0F0F0F0F0F)
        x = (x + np.uint64(0x0101010101010101)) & np.uint64(0xF0F0F0F0F0F0F0F0)
        return x - (x >> np.uint64(4))

def get_empty_mask(x):
    return get_even_empty_mask(x) | (get_even_empty_mask(x >> np.uint64(4)) << np.uint64(4))

