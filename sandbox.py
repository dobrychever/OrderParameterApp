import sys
import numpy as np


def loadBotsPositions(filename):
    try:
        return np.load(filename, allow_pickle=True).tolist()
    except IOError:
        return -1


def calculateParameter(bots_positions):
    return 'Гвоздь в жопе'


if __name__ == '__main__':
    filename = str(sys.argv[1])
    positions = loadBotsPositions(filename)
    value = calculateParameter(positions)
    print(value)
