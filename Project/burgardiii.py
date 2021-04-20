import pygame
import math
import time
import numpy
import copy
import heapq


class GridCell:
    def __init__(self, obstacle=False, explored=False):
        self.obstacle = obstacle
        self.explored = explored
        self.inrange = False
        self.hasrobot = False
        self.inpath = False
        self.destination = False
        self.frontier = False


class Robot:
    def __init__(self, position=(-1, -1), radius=5, advantage=0, gsize=50):
        self.radius = radius
        self.position = position
        self.advantage = advantage
        self.gridMemory = [[[float(i), float(j)] for i in range(gsize)] for j in range(gsize)]
        self.path = []
        self.within = []


def distance(pointa, pointb):
    return math.sqrt((pointb[0] - pointa[0]) ** 2 + (pointb[1] - pointa[1]) ** 2)


def nearby(cell):
    nlist = []
    (i, j) = cell
    if i + 1 < gridSize:
        nlist.append((i + 1, j))
        if j + 1 < gridSize:
            nlist.append((i + 1, j + 1))
        if j - 1 >= 0:
            nlist.append((i + 1, j - 1))
    if i - 1 >= 0:
        nlist.append((i - 1, j))
        if j + 1 < gridSize:
            nlist.append((i - 1, j + 1))
        if j - 1 >= 0:
            nlist.append((i - 1, j - 1))
    if j + 1 < gridSize:
        nlist.append((i, j + 1))
    if j - 1 >= 0:
        nlist.append((i, j - 1))
    return nlist.copy()


def updateUtility():
    # Update utility for each frontier cell
    # Note: This method now has O(n^3) distance function calls instead O(n^5). This is the best I can do.
    if len(frontiers) == 0:
        return
    frontierlist = list(frontiers.keys())
    frontlist = [
        [[distance((i, j), front) for front in frontierlist] for j in range(gridSize)] for i in range(gridSize)
    ]
    botlist = [[[False for k in range(len(robots))] for j in range(gridSize)] for i in range(gridSize)]

    for bot in robots:
        if len(bot.path) == 0:
            continue
        for i in range(0, gridSize):
            for j in range(0, gridSize):
                if distance((i, j), bot.path[len(bot.path) - 1]) <= bot.radius:
                    botlist[i][j][robots.index(bot)] = True

    for front in frontiers:
        ratelist = []
        for rob in robots:
            allin = set([])
            explrd = set([])
            for i in range(0, gridSize):
                for j in range(0, gridSize):
                    if frontlist[i][j][frontierlist.index(front)] <= rob.radius:
                        allin.add((i, j))
                        if grid[i][j].explored:
                            explrd.add((i, j))
            for bot in robots:
                botset = set([])
                if robots.index(rob) == robots.index(bot):
                    continue
                if len(bot.path) == 0:
                    continue
                for i in range(0, gridSize):
                    for j in range(0, gridSize):
                        if botlist[i][j][robots.index(bot)]:
                            botset.add((i, j))
                tempset = botset & allin
                explrd |= tempset
            rate = float(len(explrd)) / float(len(allin))
            ratelist.append(rate)
        frontiers[front] = ratelist.copy()


gridSize = 50
elementSize = 13
grids = []
grid = [[GridCell() for i in range(gridSize)] for j in range(gridSize)]
gnum = 0

pygame.init()
pygame.display.set_caption('Project Test 3')

running = True

windowSize = (elementSize + 1) * gridSize + 1
screen = pygame.display.set_mode((windowSize, windowSize))

robots = [
    Robot((3, 12)),
    Robot((43, 1)),
    Robot((17, 37))
]

frontiers = {}
closed = []
loopcount = 0
tstart = time.time()


def astar(start, goal):
    scoreheap = []
    openlist = []
    closelist = []
    path = []
    gscore = {}
    hscore = {}
    fscore = {}
    prevnode = {}
    gscore[start] = 0
    hscore[start] = distance(start, goal)
    fscore[start] = hscore[start]
    heapq.heappush(scoreheap, (fscore[start], start))
    openlist.append(start)

    while len(openlist) > 0:
        (lscore, nbest) = heapq.heappop(scoreheap)
        openlist.remove(nbest)
        if nbest not in closelist:
            closelist.append(nbest)
        if nbest != goal:
            nlist = nearby(nbest)
            for z in nlist:
                if grid[z[0]][z[1]].obstacle:
                    closelist.append(z)
                if z in closelist:
                    continue
                gtentative = math.sqrt((z[0] - nbest[0]) ** 2 + (z[1] - nbest[1]) ** 2) + gscore.get(nbest)
                if z not in openlist:
                    prevnode[z] = nbest
                    gscore[z] = gtentative
                    hscore[z] = math.sqrt((goal[0] - z[0]) ** 2 + (goal[1] - z[1]) ** 2)
                    fscore[z] = gscore[z] + hscore[z]
                    heapq.heappush(scoreheap, (fscore[z], z))
                    openlist.append(z)
                else:
                    if gtentative < gscore[z]:
                        prevnode[z] = nbest
                        gscore[z] = gtentative
                        fscore[z] = gscore[z] + hscore[z]
        else:
            path.append(nbest)
            while nbest is not start:
                nbest = prevnode.get(nbest)
                path.append(nbest)
            path.reverse()
            break
    return path.copy()


def visibility(first=False):
    grid[robot.position[0]][robot.position[1]].hasrobot = True
    for i in range(0, gridSize):
        for j in range(0, gridSize):
            if first:
                robot.gridMemory[i][j][0] = 999999  # cost
                robot.gridMemory[i][j][1] = -999999  # total score
            d = distance(robot.position, (i, j))
            if not grid[i][j].obstacle:
                robot.gridMemory[i][j][0] = d
            if d <= robot.radius:
                robot.within.append((i, j))
                grid[i][j].inrange = True

    remove = set([])
    for (i, j) in robot.within:
        if (i, j) in remove:
            continue
        if grid[i][j].obstacle:
            slope = (j - robot.position[1]) / (i - robot.position[0])
            upper = slope + 0.5
            lower = slope - 0.5
            for (m, n) in robot.within:
                if (m, n) == (i, j):
                    continue
                if distance(robot.position, (m, n)) > robot.radius:
                    tslope = (n - robot.position[1]) / (m - robot.position[0])
                    if lower <= tslope <= upper:
                        remove.add((m, n))
    for z in remove:
        if z in robot.within:
            robot.within.remove(z)


# Initialize the starting frame
for robot in robots:
    visibility(True)

grids.append(copy.deepcopy(grid))
print("Saved First Grid")

while True:
    loopcount += 1

    # Mark inrange cells as explored and add appropriate explored cells in frontier cell dictionary
    for i in range(0, gridSize):
        for j in range(0, gridSize):
            if grid[i][j].inrange:
                grid[i][j].explored = True

    # add appropriate explored cells in frontier cell dictionary
    for i in range(0, gridSize):
        for j in range(0, gridSize):
            if (i, j) in closed:
                continue
            if (i, j) in frontiers.keys():
                continue
            if grid[i][j].explored:
                neighbors = nearby((i, j))
                for (x, y) in neighbors:
                    if not grid[x][y].explored:
                        frontiers.update({(i, j): []})
                        break

    # Have a robot move towards its desired cell and update its sensor as long as its path is not empty
    for robot in robots:
        if len(robot.path) > 0:
            if robot.gridMemory[robot.path[0][0]][robot.path[0][1]][0] - robot.advantage <= 1:
                floored = float(math.floor(robot.advantage))
                ceiling = float(math.ceil(robot.gridMemory[robot.path[0][0]][robot.path[0][1]][0]))
                robot.advantage -= floored
                robot.advantage += ceiling - robot.gridMemory[robot.path[0][0]][robot.path[0][1]][0]
                grid[robot.position[0]][robot.position[1]].hasrobot = False
                grid[robot.path[0][0]][robot.path[0][1]].inpath = False

                for r in robots:
                    if robots.index(r) != robots.index(robot):
                        if robot.path[0] in r.path:
                            grid[robot.path[0][0]][robot.path[0][1]].inpath = True
                for (i, j) in robot.within:
                    grid[i][j].inrange = False
                    for r in robots:
                        if robots.index(r) != robots.index(robot):
                            if (i, j) in r.within:
                                grid[i][j].inrange = True
                robot.within.clear()

                robot.position = robot.path[0]
                visibility()
                robot.path.pop(0)

            else:
                robot.advantage += 1

    # Determine whether each frontier cell should stay a frontier cell
    poplist = []

    for (i, j) in frontiers.keys():
        flag = False
        neighbors = nearby((i, j))
        for (x, y) in neighbors:
            if not grid[x][y].explored:
                flag = True
                break
        if not flag:
            poplist.append((i, j))
        grid[i][j].frontier = flag

    for p in poplist:
        frontiers.pop(p)
        closed.append(p)

    # If a robot has an empty path, have it find a new frontier cell and calculate the path to it with A*
    for robot in robots:
        if len(robot.path) == 0:
            updateUtility()
            grid[robot.position[0]][robot.position[1]].frontier = False
            grid[robot.position[0]][robot.position[1]].destination = False
            if len(frontiers) == 0:
                break
            tdict = {}
            for frontier in frontiers:
                (i, j) = frontier
                r = frontiers[frontier][robots.index(robot)]
                utility = (1 - r) * (robot.radius ** 2)
                tdict.update({utility - robot.gridMemory[i][j][0]: frontier})
            bestscore = max(tdict.keys())
            frontier = tdict[bestscore]
            frontiers.pop(frontier)
            closed.append(frontier)
            robot.path = astar(robot.position, frontier)
            grid[robot.path[len(robot.path) - 1][0]][robot.path[len(robot.path) - 1][1]].destination = True
            for p in robot.path:
                grid[p[0]][p[1]].inpath = True

    # Break out of loop if all the robots stopped moving (successful results)
    done = True
    for robot in robots:
        if len(robot.path) > 0:
            done = False
    if done:
        grids.append(copy.deepcopy(grid))
        print("Saved Last Grid")
        break

    # Break out of loop after loopcount reaches a relatively high number (unsuccessful results)
    if loopcount == 500:
        print("Too many grids: solution not found!")
        break

    # Save the state of the grid to a list of grids
    grids.append(copy.deepcopy(grid))
    print("Saved Grid: " + str(len(grids)))

tstop = time.time()

print("Total number of steps: " + str(len(grids)))
print("Total time in seconds: " + str(tstop - tstart))

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
            if g[i][j].inpath:
                color = (255, 255, 0)
            # if g[i][j].frontier:
            #     color = (0, 255, 255)
            if g[i][j].destination:
                color = (255, 128, 0)
            if g[i][j].hasrobot:
                color = (255, 0, 0)
            pygame.draw.rect(frame, color, block)

    pygame.transform.scale(frame, screen.get_size(), screen)
    pygame.display.flip()

    time.sleep(0.25)

pygame.quit()
