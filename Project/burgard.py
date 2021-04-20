import pygame
import math
import time
import numpy
import copy


class GridCell:
    def __init__(self, obstacle=False, explored=False, inrange=False, hasrobot=False):
        self.obstacle = obstacle
        self.explored = explored
        self.inrange = inrange
        self.hasrobot = hasrobot


class Robot:
    def __init__(self, position=(-1, -1), radius=5, gsize=50):
        self.radius = radius
        self.position = position
        self.gridMemory = [[[float(i), float(j)] for i in range(gsize)] for j in range(gsize)]


def distance(pointa, pointb):
    return math.sqrt((pointb[0] - pointa[0]) ** 2 + (pointb[1] - pointa[1]) ** 2)


gridSize = 50
elementSize = 13
grids = []
grid = [[GridCell() for i in range(gridSize)] for j in range(gridSize)]
gnum = 0

pygame.init()
pygame.display.set_caption('Project Test 1')

running = True

windowSize = (elementSize + 1) * gridSize + 1
screen = pygame.display.set_mode((windowSize, windowSize))

# Step 1: initialize robots
robots = [
    Robot((3, 12)),
    Robot((43, 1)),
    Robot((17, 37))
]

# Step 2: initialize the starting frame
for robot in robots:
    (x, y) = robot.position
    grid[x][y].hasrobot = True
    for i in range(0, gridSize):
        for j in range(0, gridSize):
            robot.gridMemory[i][j][0] = 999999  # cost
            robot.gridMemory[i][j][1] = -999999  # total score
            d = distance((x, y), (i, j))
            if not grid[i][j].obstacle:
                robot.gridMemory[i][j][0] = d
            if d <= robot.radius:
                grid[i][j].inrange = True
grids.append(copy.deepcopy(grid))
print("Saved First Grid")


frontiers = {}
closed = []
loopcount = 0

while True:
    loopcount += 1
    # Step 3: Mark inrange cells as explored and add appropriate explored cells in frontier cell dictionary
    for i in range(0, gridSize):
        for j in range(0, gridSize):
            if grid[i][j].inrange:
                grid[i][j].explored = True

    for i in range(0, gridSize):
        for j in range(0, gridSize):
            if (i, j) in closed:
                continue
            if (i, j) in frontiers.keys():
                continue
            if grid[i][j].explored:
                flag = False
                for x in range(0, gridSize):
                    for y in range(0, gridSize):
                        if not grid[x][y].explored:
                            for robot in robots:
                                if robot.position != (i, j):
                                    if distance((x, y), (i, j)) <= robot.radius:
                                        frontiers.update({(i, j): None})
                                        flag = True
                                if flag:
                                    break
                        if flag:
                            break
                    if flag:
                        break

    if len(frontiers) == 0:
        break

    # Step 4: Update utility for each frontier cell
    for frontier in frontiers:
        (x, y) = frontier
        costsum = float(0)
        for robot in robots:
            costsum += robot.gridMemory[x][y][0]
        frontiers[frontier] = costsum / len(robots)

    # Step 5: Move robots to best frontier cell
    for robot in robots:
        tdict = {}
        for frontier in frontiers:
            (x, y) = frontier
            tdict.update({frontiers[frontier] - robot.gridMemory[x][y][0]: frontier})
        if len(tdict) == 0:
            break
        bestscore = max(tdict.keys())
        grid[robot.position[0]][robot.position[1]].hasrobot = False
        for i in range(0, gridSize):
            for j in range(0, gridSize):
                if distance(robot.position, (i, j)) <= robot.radius:
                    grid[i][j].inrange = False
        robot.position = tdict[bestscore]
        frontiers.pop(tdict[bestscore])
        closed.append(tdict[bestscore])
        (x, y) = robot.position
        grid[x][y].hasrobot = True
        for i in range(0, gridSize):
            for j in range(0, gridSize):
                d = distance((x, y), (i, j))
                if not grid[i][j].obstacle:
                    robot.gridMemory[i][j][0] = d
                if d <= robot.radius:
                    grid[i][j].inrange = True

    flag = False
    poplist = []
    for frontier in frontiers:
        for robot in robots:
            for i in range(0, gridSize):
                for j in range(0, gridSize):
                    if distance(frontier, (i, j)) <= robot.radius:
                        if not grid[i][j].explored:
                            flag = True
                            break
                    if flag:
                        break
                if flag:
                    break
            if flag:
                break
        if not flag:
            poplist.append(frontier)

    for p in poplist:
        frontiers.pop(p)

    grids.append(copy.deepcopy(grid))
    print("Saved Grid: " + str(len(grids)))

frame = pygame.Surface((windowSize, windowSize))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    gnum += 1
    g = None

    if gnum > len(grids):
        g = grids[len(grids) - 1]
        gnum = len(grids)
    else:
        g = grids[gnum - 1]

    frame.fill((0, 0, 0))
    screen.fill((0, 0, 0))

    for i in range(0, gridSize):
        for j in range(0, gridSize):
            block = pygame.Rect((i * (elementSize + 1)) + 1, (j * (elementSize + 1)) + 1, elementSize, elementSize)
            color = (255, 255, 255)
            if g[i][j].obstacle:
                color = numpy.subtract(color, (100, 100, 100))
            if g[i][j].inrange:
                color = numpy.subtract(color, (50, 0, 50))
            if g[i][j].explored:
                color = numpy.subtract(color, (50, 50, 0))
            if g[i][j].hasrobot:
                color = (255, 0, 0)
            pygame.draw.rect(frame, color, block)

    pygame.transform.scale(frame, screen.get_size(), screen)
    pygame.display.flip()

    time.sleep(0.25)

pygame.quit()
