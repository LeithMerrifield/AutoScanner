from src import Elements


class State:
    """
    Used to hold the current state and all possible states

    Attributes
    ----------
    current_state : int
        Integer key of state the relates to state_dict
    state_dict : dict
        Holds all possible page states from start of mobile emulator to the picking screen

    Methods
    -------
    get_index(order=None)
        returns current_state

    change_state(state: string)
        Changes current_state to the passed in state index

    login()
        Logs in and navigates to the WMS order list

    """

    def __init__(self) -> None:
        self.current_state = 1
        # self.state_dict = {1: stage[0], 2: stage[1], 3: stage[2], 4: stage[3],5:stage[4],6:stage[5],7:stage[6]}
        self.state_dict = Elements.STAGEDICT

    def get_index(self):
        return self.current_state

    def change_state(self, state):
        """
        Takes the string value of the current page and sets the current_index to it's index
        """
        self.current_state = self.state_dict[state]
        pass
