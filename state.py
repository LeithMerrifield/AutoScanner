import Elements

class State:
    def __init__(self) -> None:
        stage = Elements.STAGE
        self.currentState = 1
        # self.stateDict = {1: stage[0], 2: stage[1], 3: stage[2], 4: stage[3],5:stage[4],6:stage[5],7:stage[6]}
        self.stateDict = Elements.STAGEDICT

    def getIndex(self):
        return self.currentState
    
    def changeState(self,state):
        self.currentState = self.stateDict[state]
        pass