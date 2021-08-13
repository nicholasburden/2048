import numpy as np
from game_model import Action, transpose_board
import bisect

DEPTH = 5 # Depth of search tree (counting both player and adversary nodes)

class BitboardAgent:
	def __init__(self, heuristic_lookup=None):
		self.direction = Action.Up
		if heuristic_lookup:
			self.heuristic_lookup = heuristic_lookup
		else:
			self.heuristic_lookup = get_heuristic_lookup()

	def get_move(self, model):
		seen_states = []
		score = -float('inf')
		best_action = Action.Up
		for action in Action:
			new_model = model.clone()
			moved = new_model.move(action)
			if moved:
				x = self.expectiminimax(new_model, DEPTH-1, False, seen_states, 1)
				if x > score:
					best_action = action
					score = x
		return best_action

	def expectiminimax(self, model, depth, is_player, seen_states, probability):
		if is_in_sorted_list(seen_states, model.board) or depth == 0 or probability < 0.001:
			# TODO: Consider caching heuristic result of seen before states. Should be possible as search is depth first
			bisect.insort(seen_states, model.board)
			return calculate_heuristic(model.board, self.heuristic_lookup)
		# TODO: Make seen_states more efficient by using a heap 
		bisect.insort(seen_states, model.board)
		if is_player:
			score = -float('inf')
			for action in Action:
				new_model = model.clone()
				moved = new_model.move(action)
				if moved:
					score = max(score, self.expectiminimax(new_model, depth-1, False, seen_states, probability))
			return score
		else:
			score = float('inf')
			n_empty = model.num_empty()
			probability = probability / n_empty
			for i in range(n_empty):
				model_2 = model.clone()
				model_4 = model.clone()
				model_2.add_tile_at_pos(2, i)
				model_4.add_tile_at_pos(4, i)
				score_2 = self.expectiminimax(model_2, depth-1, True, seen_states, probability * 0.9)
				score_4 = self.expectiminimax(model_4, depth-1, True, seen_states, probability * 0.1)
				score = min(score, 0.9 * score_2 + 0.1 * score_4)
			return score

def calculate_heuristic(board, heuristic_lookup):
	heur = 0
	for i in range (4):
		row = (board >> np.uint64((i * 16))) & np.uint64(0xFFFF)
		heur += heuristic_lookup[row]
	board = transpose_board(board)
	for i in range (4):
		row = (board >> np.uint64((i * 16))) & np.uint64(0xFFFF)
		heur += heuristic_lookup[row]
	return heur

def get_heuristic_lookup():
	heur_score_table = {}
	for row in range(65536):
		sum = 0
		empty = 0
		merges = 0
		prev = 0
		counter = 0
		line = [row & 0xF, row >> 4 & 0xF, row >> 8 & 0xF, row >> 12 & 0xF]
		for i in range(4):
			rank = line[i]
			sum += pow(rank, 2)
			if (rank == 0):
				empty += 1
			else:
				if (prev == rank):
					counter += 1
				elif (counter > 0):
					merges += 1 + counter
					counter = 0
				
				prev = rank
		if (counter > 0):
			merges += 1 + counter

		monotonicity_left = 0
		monotonicity_right = 0
		for i in range(1, 4, 1):
			if (line[i-1] > line[i]):
				monotonicity_left += pow(line[i-1], 2) - pow(line[i], 2)
			else:
				monotonicity_right += pow(line[i], 2) - pow(line[i-1], 2)

		#Parameters chosen by rough trial and error
		# TODO: tune parameters using some form of automated search
		heur_score_table[row] = 300 * empty + 500 * merges - 50 * min(monotonicity_left, monotonicity_right) + 10 * sum

	return heur_score_table

def is_in_sorted_list(a, x):
    pos = bisect.bisect_left(a, x, 0, len(a))
    return pos != len(a) and a[pos] == x
