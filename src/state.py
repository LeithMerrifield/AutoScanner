from src import Elements


class State:
    def __init__(self) -> None:
        self.current_state = 1
        # self.state_dict = {1: stage[0], 2: stage[1], 3: stage[2], 4: stage[3],5:stage[4],6:stage[5],7:stage[6]}
        self.state_dict = Elements.STAGEDICT

    def get_index(self):
        return self.current_state

    def change_state(self, state):
        self.current_state = self.state_dict[state]
        pass
