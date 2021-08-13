
from game_model import Model
import math
import csv

def init_tables():
    with open('row_merge_lookup.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["before", "after"])
        for x in range(2**16):
            row = convert_to_row(x)
            merge_right(row)
            new_number = convert_to_16_bit(row)
            csvwriter.writerow([x, new_number])

def convert_to_16_bit(row):
    for i in range(4):
        if row[i] != 0:
            row[i] = int(math.log2(row[i]))
        row[i] = row[i] << (4*(4-i-1))
       
    return sum(row)

def convert_to_64_bit(mat):
    row_nums = []
    for i in range(4):
        row_nums.append(convert_to_16_bit(mat[i]))
    for i in range(4):
        row_nums[i] = row_nums[i] << (16*(4-i-1))
    return sum(row_nums)

#print(convert_to_16_bit([2,3,4,5]))

#print(convert_to_16_bit([2,3,4,5]))

def get_row(num, i):
    mask = 0xFFFF << (16*(4-i-1))
    num = num & mask
    return num >> (16*(4-i-1))


def get_item(num, i):
    mask = 0xF << (4*(4-i-1))
    num = num & mask
    num = num >> (4*(4-i-1))
    if num == 0:
        return 0
    return 2** num 

#print(get_row(9029, 3))


def transpose_board(x):
	a1 = x & 0xF0F00F0FF0F00F0F
	a2 = x & 0x0000F0F00000F0F0
	a3 = x & 0x0F0F00000F0F0000
	a = a1 | (a2 << 12) | (a3 >> 12)
	b1 = a & 0xFF00FF0000FF00FF
	b2 = a & 0x00FF00FF00000000
	b3 = a & 0x00000000FF00FF00
	return b1 | (b2 >> 24) | (b3 << 24)


def convert_to_grid(num):
    grid = []
    for i in range(4):
        row = []
        row_num = get_row(num, i)
        for j in range(4):
            item = get_item(row_num, j)
            row.append(item)
        grid.append(row)
    return grid

def convert_to_row(num):

    row = []
    for j in range(4):
        item = get_item(num, j)
        row.append(item)
    return row

def reverse_row(row_num):
    a_1 = (row_num & 0xF000) >> 12
    a_2 = (row_num & 0x0F00) >> 4
    a_3 = (row_num & 0x00F0) << 4
    a_4 = (row_num & 0x000F) << 12
    return a_1 | a_2 | a_3 | a_4

def merge_right(row):
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

def load_csv():
    with open('row_merge_lookup.csv', 'r') as csvfile:
        lookup_table = {}
        csv_reader = csv.DictReader(csvfile)
        line_count = 0
        
        for row in csv_reader:
            #print(row)
            lookup_table[int(row["before"])] = int(row["after"])
            #print(f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
            #line_count += 1
        #print(f'Processed {line_count} lines.')
    return lookup_table
#init_tables()


class Model:
    """
    Board represented as a 64 bit int, each nibble x representing a single cell 2^x
    """

    def __init__(self):
        self.merge_lookup = {}
        for x in range(2**16):
            row = convert_to_row(x)
            #print(row)
            merge_right(row)
            new_number = convert_to_16_bit(row)
            self.merge_lookup[x] = new_number
     
    def merge_right(self, board):
        merged_rows = []
        for i in range(4):
            merged_rows.append(self.merge_lookup[get_row(board, i)])
        for i in range(4):
            merged_rows[i] = merged_rows[i] << (16*(4-i-1))
        return sum(merged_rows)

    def merge_left(self, board):
        merged_rows = []
        for i in range(4):
            merged_rows.append(reverse_row(self.merge_lookup[reverse_row(get_row(board, i))]))
        for i in range(4):
            merged_rows[i] = merged_rows[i] << (16*(4-i-1))
        return sum(merged_rows)
    
    def merge_down(self, board):
        board = transpose_board(board)
        board = self.merge_right(board)
        return transpose_board(board)

    def merge_up(self, board):
        board = transpose_board(board)
        board = self.merge_left(board)
        return transpose_board(board)







#load_csv()

model = Model()
print(convert_to_16_bit([2,2,2,2]))
print(convert_to_grid(model.merge_right(convert_to_64_bit([[2,2,2,2],
                                                          [4,2,4,2], 
                                                          [4,2,2,2],
                                                          [4,2,4,4]]))))
