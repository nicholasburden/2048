from game_view import BitboardView, View
from game_model import BitboardModel, Action
from ai import BitboardAgent
import numpy as np

SIZE = 4
ODDS_OF_4 = 0.1

class Game:
    def __init__(self):
        self.model = BitboardModel()
        self.model.add_random_tile()
        self.model.add_random_tile()
        self.view = BitboardView()
        self.agent = BitboardAgent()
        self.view.render(self.model.board)
        self.view.root.bind("<Key>", self.key_handler)
        self.view.root.mainloop()

    def key_handler(self, event):
        key_value = event.keysym
        moved = False
        if key_value in View.UP_KEYS:
            moved = self.model.move(Action.Up)
        elif key_value in View.LEFT_KEYS:
            moved = self.model.move(Action.Left)
        elif key_value in View.DOWN_KEYS:
            moved = self.model.move(Action.Down)
        elif key_value in View.RIGHT_KEYS:
            moved = self.model.move(Action.Right)
        elif key_value in View.SPACE_KEYS:
            moved = self.model.move(self.agent.get_move(self.model))
        else:
            pass
        if moved:
            self.model.add_random_tile()
        self.view.render(self.model.board)

if __name__ == "__main__":
    game=Game()
