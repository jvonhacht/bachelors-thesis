from entities import Direction

class PrioSNScheduler:
    def __init__(self, simulator):
        self.simulator = simulator

    def schedule(self):
        return 0

    def __str__(self):
        return 'Prioritise SOUTH/NORTH scheduler'
