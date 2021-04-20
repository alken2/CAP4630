import pygame
import math
import heapq

# Step 0.1: implement a Graph class
# This Graph implementation is based on the following source:
# https://www.tutorialspoint.com/python_data_structure/python_graphs.htm


class Graph:
    def __init__(self, gdict=None):
        if gdict is None:
            gdict = {}
        self.gdict = gdict

    def neighbors(self, v):
        return self.gdict[v].copy()

    def vertices(self):
        vlist = []
        for v in self.gdict:
            vlist.append(v)
        return vlist

    def edges(self):
        elist = []
        for v in self.gdict:
            for nextv in self.gdict[v]:
                if {v, nextv} not in elist:
                    elist.append({v, nextv})
        return elist

    def addVertex(self, v):
        if v not in self.gdict:
            self.gdict.update({v: []})

    def addEdge(self, e):
        e = set(e)
        (v1, v2) = tuple(e)
        if v1 in self.gdict:
            if v2 not in self.gdict[v1]:
                self.gdict[v1].append(v2)
        else:
            self.gdict[v1] = [v2]
        if v2 in self.gdict:
            if v1 not in self.gdict[v2]:
                self.gdict[v2].append(v1)
        else:
            self.gdict[v2] = [v1]

# Step 0.2: declare some functions
# The onSegment, orientation, and checkIntersection functions are based on the following source:
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/


def onSegment(p, q, r):
    if ((q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and
            (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
        return True
    return False


def orientation(p, q, r):
    val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))
    if val > 0:
        return 1
    elif val < 0:
        return 2
    else:
        return 0


def checkIntersection(e1, e2):
    o1 = orientation(e1[0], e1[1], e2[0])
    o2 = orientation(e1[0], e1[1], e2[1])
    o3 = orientation(e2[0], e2[1], e1[0])
    o4 = orientation(e2[0], e2[1], e1[1])

    if (o1 != o2) and (o3 != o4):
        return True

    if (o1 == 0) and onSegment(e1[0], e2[0], e1[1]):
        return True

    if (o2 == 0) and onSegment(e1[0], e2[1], e1[1]):
        return True

    if (o3 == 0) and onSegment(e2[0], e1[0], e2[1]):
        return True

    if (o4 == 0) and onSegment(e2[0], e1[1], e2[1]):
        return True

    return False


def distance(pointa, pointb):
    return math.sqrt((pointb[0] - pointa[0]) ** 2 + (pointb[1] - pointa[1]) ** 2)


def positionv(v):
    return v[0] + 8, v[1] + 8


def positionp(polygon):
    for i in range(0, len(polygon)):
        polygon[i] = positionv(polygon[i])
    return polygon


def drawenv(surface, showv=True, dclose=False, dopen=False, dallowed=False, dpath=True, dpolygons=True, dsg=True):
    (od, cd, pd, gd) = buildgraph()
    opengraph = Graph(od)
    closegraph = Graph(cd)
    pathgraph = Graph(pd)
    fullgraph = Graph(gd)

    if dpolygons:  # Draw polygons
        for polygon in polygons:
            pygame.draw.polygon(surface, (0, 0, 0), positionp(polygon.copy()), 3)

    if dallowed:  # Draw allowed graph edges
        for segment in fullgraph.edges():
            pygame.draw.line(surface, (255, 255, 0), positionv(list(segment)[0]), positionv(list(segment)[1]), 1)
            if showv:
                pygame.draw.circle(surface, (255, 255, 0), positionv(list(segment)[0]), 2)
                pygame.draw.circle(surface, (255, 255, 0), positionv(list(segment)[1]), 2)

    if dopen:  # Draw open edges
        for segment in opengraph.edges():
            pygame.draw.line(surface, (0, 255, 255), positionv(list(segment)[0]), positionv(list(segment)[1]), 1)
            if showv:
                pygame.draw.circle(surface, (0, 255, 255), positionv(list(segment)[0]), 2)
                pygame.draw.circle(surface, (0, 255, 255), positionv(list(segment)[1]), 2)

    if dclose:  # Draw closed edges
        for segment in closegraph.edges():
            pygame.draw.line(surface, (255, 0, 255), positionv(list(segment)[0]), positionv(list(segment)[1]), 1)
            if showv:
                pygame.draw.circle(surface, (255, 0, 255), positionv(list(segment)[0]), 2)
                pygame.draw.circle(surface, (255, 0, 255), positionv(list(segment)[1]), 2)

    if dpath:  # Draw path edges
        for segment in pathgraph.edges():
            pygame.draw.line(surface, (0, 255, 0), positionv(list(segment)[0]), positionv(list(segment)[1]), 2)
            if showv:
                pygame.draw.circle(surface, (0, 255, 0), positionv(list(segment)[0]), 3)
                pygame.draw.circle(surface, (0, 255, 0), positionv(list(segment)[1]), 3)

    if dsg:  # Draw start and goal points
        pygame.draw.circle(surface, (255, 0, 0), positionv(start), 5)
        pygame.draw.circle(surface, (0, 0, 255), positionv(goal), 5)


def choosePolyEnv(polyenv):
    return {
        1: (polyenvone.copy(), (162, 352), (849, 29)),
        2: (polyenvtwo.copy(), (119, 444), (903, 77))
    }.get(polyenv, (polyenvone.copy(), (162, 352), (849, 29)))


# Step 0.3: declare initially required variables

# As of submission, only convex polygons are supported. For information on convex polygons, see the following source:
# https://en.wikipedia.org/wiki/Convex_polygon
polyenvone = [
    [(158, 119), (177, 222), (287, 247), (346, 116), (272, 16)],
    [(191, 296), (509, 296), (509, 397), (191, 397)],
    [(351, 255), (392, 98), (438, 255)],
    [(445, 151), (445, 25), (523, 15), (578, 72)],
    [(524, 204), (621, 285), (555, 347)],
    [(596, 234), (596, 27), (728, 27), (728, 234)],
    [(672, 292), (743, 244), (798, 292), (798, 370), (734, 402), (672, 365)],
    [(746, 53), (794, 24), (831, 62), (812, 251)]
]

polyenvtwo = [
    [(129, 103), (144, 411), (177, 399), (383, 205), (202, 74)],
    [(188, 446), (509, 403), (509, 296), (191, 394)],
    [(375, 237), (402, 176), (751, 176), (724, 237)],
    [(487, 263), (641, 245), (594, 393)],
    [(729, 455), (771, 42), (802, 475)],
    [(797, 229), (900, 229), (900, 126), (797, 126)]
]


def getInput():
    userinput = [
        int(input("Select an environment (type 1 or 2 to select environment): ")),
        float(input("Enter a number for the constraint for the PTS algorithm: "))
    ]
    return choosePolyEnv(userinput[0])[0], choosePolyEnv(userinput[0])[1], choosePolyEnv(userinput[0])[2], userinput[1]


edgelist = []
blacklist = []


# Step 1.1: add all graph vertices and initial graph edges grabbed from polygons
def buildgraph():
    edgelist.clear()
    blacklist.clear()
    g = Graph()
    g.addVertex(start)
    g.addVertex(goal)
    for poly in polygons:
        for point in poly:
            g.addVertex(point)
            index = poly.index(point)
            if index > 0:
                g.addEdge([point, poly[index - 1]])
                if index is len(poly) - 1:
                    g.addEdge([point, poly[0]])

    # Step 1.2: fill edgelist with all possible edges except internal polygon edges
    for vertex1 in g.vertices():
        for vertex2 in g.vertices():
            flag = True
            if vertex1 == vertex2:
                continue
            for poly in polygons:
                if all([vertex1 in poly, vertex2 in poly]):
                    flag = False
                    break
            if flag is True:
                if {vertex1, vertex2} not in edgelist:
                    edgelist.append({vertex1, vertex2})

    # Step 1.3: fill blacklist with edges from edgelist that intersect with edges that are already in the graph
    for edge1 in edgelist:
        for edge2 in g.edges():
            if edge1 in blacklist:
                continue
            if edge1 == edge2:
                continue
            if (list(edge1)[0] == list(edge2)[0]) or (list(edge1)[1] == list(edge2)[1]) or \
                    (list(edge1)[0] == list(edge2)[1]) or (list(edge1)[1] == list(edge2)[0]):
                continue
            if checkIntersection(list(edge1), list(edge2)):
                blacklist.append(edge1)

    # Step 1.4: add all edges from edgelist to the graph except edges that appear in blacklist
    for edge in edgelist:
        if edge in blacklist:
            continue
        else:
            g.addEdge(list(edge))

    # Step 1.5: print details of edgelist, blacklist, and edges of Graph g
    print()
    print("All Possible Edges (Except Internal Polygon Edges): ")
    print(edgelist)
    print("Edge Blacklist: ")
    print(blacklist)
    print("Allowed Graph Edges: ")
    print(g.edges())

    # Step 1.6: call pts function and print details of open edges, closed edges, path edges, and sorted path vertices
    (opend, closed, pathd) = pts(g.gdict.copy())

    print()
    print("Open Edges: ")
    print(Graph(opend).edges())
    print("Closed Edges: ")
    print(Graph(closed).edges())
    print("Path Edges: ")
    print(Graph(pathd).edges())
    print()
    if len(Graph(pathd).vertices()) > 1:
        print("Path Vertices (In Order of Start -> Goal): ")
        print(Graph(pathd).vertices())
    else:
        print("No Path Between Start and Goal Available!")
    print()

    return opend.copy(), closed.copy(), pathd.copy(), g.gdict.copy()


# Step 2.1: create the required variables for the potential search (PTS) algorithm
def pts(gdict):
    g = Graph(gdict)
    newscoreheap = []
    openlist = []
    closelist = []
    path = []

    gscore = {}
    hscore = {}
    uscore = {}
    prevnode = {}

    gscore[start] = 0
    hscore[start] = distance(start, goal)
    uscore[start] = (costbound - gscore[start])/hscore[start]
    heapq.heappush(newscoreheap, (-uscore[start], start))
    openlist.append(start)

    # Step 2.2: perform the PTS algorithm on Graph g
    while len(openlist) > 0:  # While openlist (O) is not empty
        (hiscore, nbest) = heapq.heappop(newscoreheap)  # Pick and remove the best node (nbest) from scoreheap
        openlist.remove(nbest)  # Remove nbest from openlist
        if nbest not in closelist:  # If nbest is not already in closelist (C)
            closelist.append(nbest)  # Add nbest to C
        # if nbest != goal:  # If nbest is not the goal
        nlist = g.neighbors(nbest)  # Store all neighbor nodes of nbest in nlist
        for x in nlist:  # For all neighbors (x) in nlist
            if x in closelist:  # If x appears in C
                continue  # Ignore it
            if x in openlist:  # If x is already in O
                if gscore[x] <= distance(nbest, x) + gscore.get(nbest):  # If the current g-score of x is lower or equal
                    continue  # Ignore x if duplicate is detected and its current g-score is better
            # Update g-score of x = distance between x and nbest + g-score of nbest = d(nbest, x) + g(nbest)
            gscore[x] = distance(nbest, x) + gscore.get(nbest)
            hscore[x] = distance(x, goal)
            if gscore[x] + hscore[x] >= costbound:  # Prune node over bound
                continue  # Ignore x if path is out of bound
            prevnode[x] = nbest  # Establish nbest as the previous node of x
            if x is goal:
                path.append(x)  # Start retracing the path from goal by appending x to path
                while x is not start:  # While x is not the start node
                    x = prevnode.get(x)  # Set x equal the the previous node of x
                    path.append(x)  # Append x to path
                path.reverse()  # Reverse path order from goal -> start to start -> goal
                break  # No work left to do, break out of algorithm
            if x in openlist:  # If x is already in O
                uscore[x] = (costbound - gscore[x]) / hscore[x]  # u-score of x = (C - g(x))/h(x)
            else:  # If x does appear in O
                uscore[x] = (costbound - gscore[x])/hscore[x]  # u-score of x = (C - g(x))/h(x)
                heapq.heappush(newscoreheap, (-uscore[x], x))  # Push (u-score of x, x) in newscoreheap
                openlist.append(x)  # Append x to O
        if len(path) > 0:  # If there is a path
            break  # No work left to do, break out of algorithm

    # Step 2.3: construct opened, closed, and path graphs using previous nodes
    opendict = {}
    closedict = {}
    pathdict = {}

    for o in openlist:
        opendict.update({o: [prevnode.get(o)]})

    for c in closelist:
        if prevnode.get(c) is not None:
            closedict.update({c: [prevnode.get(c)]})

    if len(path) > 1:
        pathdict.update({path[0]: []})
        for index in range(1, len(path)):
            pathdict.update({path[index]: [path[index - 1]]})

    return opendict.copy(), closedict.copy(), pathdict.copy()


# Step 3.1: initialize necessary pygame elements and set Surface environment boundaries
pygame.init()
pygame.display.set_caption('Assignment 2')

running = True
screen = pygame.display.set_mode((1280, 720))

# Step 3.2: display the results of the algorithm by drawing the environment and scaling it to the window
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

    screen.fill((255, 255, 255))

    exitinput = input("Would you like to run the program? (enter 'y' or 'n', default = 'y'): ")
    if exitinput == 'n' or exitinput == 'N':
        exit()

    (polygons, start, goal, costbound) = getInput()

    # Note to whom it may concern: pass in up to seven additional True/False arguments in drawenv for more results!
    drawenv(screen)

pygame.quit()
