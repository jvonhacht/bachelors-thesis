from entities import Direction

class PrioWEScheduler:
    def __init__(self, simulator):
        self.simulator = simulator

    def schedule(self):
        return 1

    def __str__(self):
        return 'Prioritise WEST/EAST scheduler'
