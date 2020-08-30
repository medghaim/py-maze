import time
from collections import deque
from math import hypot
from random import shuffle, randint

from blessings import Terminal

# blessings Terminal
term = Terminal()

# grid parts
CORNER = "+"
WALL = "|"
CEILING = "-"
EMPTY = " "
START = term.green + "S" + term.normal
END = term.red + "E" + term.normal

def make_maze(w = 16, h = 8, print_progress=False):
    """
    Generate the maze itself:
        1. Generate initial boundaries/grid
        2. Generate distant start/end points.
        3. DFS to traverse the grid, carving out paths as we pass through cells
        4. Add the start and end points to the grid
    """
    if w < 2 or h < 2:
        raise ValueError("maze dimension too small")

    visited = generate_boundaries(w, h)
    vertical, horizontal = generate_grid(w, h)

    start, end = get_distant_points(w, h)

    # DFS to "carve" out the maze randomly
    dfs(vertical, horizontal, visited, start, end, print_progress)

    # mark start and end positions
    s = vertical[start[1]][start[0]]
    vertical[start[1]][start[0]] = "{}{}{}".format(s[0], START, s[2])
    e = vertical[end[1]][end[0]]
    vertical[end[1]][end[0]] = "{}{}{}".format(e[0], END, e[2])
    
    # generate maze string
    return get_maze_string(vertical, horizontal)


def generate_boundaries(w, h):
    """
    Generated visited matrix where all grid points are marked as unvisited.
    Create extra row to the right, and bottom and mark as visited to act as
    boundaries prevents the DFS from wrapping around the grid.
    """
    return [[0]*w + [1] for _ in range(h)] + [[1] * (w + 1)]

def generate_grid(w, h):
    """
    Generate the full grid, split into vertical (walls and spaces), and
    horizontal (corners and ceilings). The initial state of each cell is
    completely blocked from all sides.
    """
    # generate full grid, extra column for right edge, extra row for bottom edge
    vertical   = [[get_grid_part(part=WALL)]*w + [WALL] for i in range(h)] + [[]]
    horizontal = [[get_grid_part()]*w + [CORNER] for i in range(h + 1)]

    return vertical, horizontal

def get_grid_part(part=CORNER, path=False):
    """
    Retrieves either a vertical or horizontal grid part. If part is CORNER,
    then we generate a horizontal part, if it is WALL then we generate a
    vertical part. If path is False (used when generating the initial grid), we
    generate a fully blocked cell. If path is True, we generate a grid part we
    can pass through.
    """
    if part not in [CORNER, WALL]:
        raise ValueError("unknown part: '{}'".format(part))

    rest = CEILING if not path else EMPTY 
    if part == WALL:
        part = WALL if not path else EMPTY
        rest = EMPTY
    return "{0}{1}{1}".format(part, rest)

def get_distant_points(w, h):
    """
    Randomly generate start and end points, and ensure they are decently far
    away enough from one another. To ensure distance, we compare
    distance of the randomly generated start and end points to the distance of
    the whole grid, and keep regenerating start/end points until they satisfy
    the distance requirement. We want the points to be at least 4/5ths the
    distance of the whole grid.
    """
    start = get_random_pos(w, h)
    end   = get_random_pos(w, h)
    
    # - 3 is an arbitrary value to have this play nicely with smaller w,h values
    distance_threshold = ((4*get_distance([0,0], [w, h])) / 5) - 3
    while get_distance(start, end) < distance_threshold:
        start = get_random_pos(w, h)
        end   = get_random_pos(w, h)
    return start, end

def get_random_pos(w, h):
    """
    Randomly generate a valid [x, y] position on the grid
    """
    return [randint(0, w-1), randint(0, h-1)]

def get_distance(x, y):
    """
    Compute the distance between two sets of points [x1, y1] and [x2, y2]
    """
    return hypot(y[1] - x[1], y[0] - x[0])

def dfs(vertical, horizontal, visited, start, end, print_progress):
    """
    Iterative DFS to avoid hitting maximum recursion stack depth.
    The DFS carves out the path of every adjacent neighbor we pass through.
    The stack contains sets of (prev_x, prev_y, x, y) so we can determine which
    direction we came from for each iteration, in order to path through the
    appropriate wall/ceiling.
    print_progress allows us to print (in place) the progress of the DFS/maze pathing
    every iteration.
    """
    # initialize stack with starting pos + all neighbors
    stack = deque([(start[0], start[1], adj[0], adj[1]) for adj in get_neighbors(start[0], start[1])])
    visited[start[1]][start[0]] = 1

    while stack:
        prev_x,prev_y, x,y = stack.pop()
        if not visited[y][x]:
            visited[y][x] = 1

            # carve out walls / ceilings we pass through
            if x == prev_x: # we went up/down
                horizontal[max(prev_y, y)][prev_x] = get_grid_part(path=True)
            elif y == prev_y: # we went left/right
                vertical[prev_y][max(prev_x, x)] = get_grid_part(part=WALL, path=True)

            # backtrack if we reach end
            if [x, y] == end:
                continue

            if print_progress:
                with term.hidden_cursor():
                    with term.location(0, 1):
                        print(get_maze_string(vertical, horizontal))
                time.sleep(0.0025)

            # add unvisited neighbors
            for next_x, next_y in get_neighbors(x, y):
                if not visited[next_y][next_x]:
                    stack.append((x, y, next_x, next_y))

def get_neighbors(x, y):
    """
    Given an [x,y] point on the grid, return a list of the adjacent neighbors.
    For each position on the board, the adjacent neighbors will be up/down/left/right.
    We shuffle this list in order to randomize the pathing in the DFS.
    """
    neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
    shuffle(neighbors)
    return neighbors

def get_maze_string(vertical, horizontal):
    """
    Combine horizontal and vertical lists in order to generate a single string
    which represents the entirety of the grid.
    """
    maze = ""
    for (h, v) in zip(horizontal, vertical):
        maze += ''.join(h + ['\n'] + v + ['\n'])
    return maze[:-1]

if __name__ == '__main__':
    print(make_maze(70,40, print_progress=True))
