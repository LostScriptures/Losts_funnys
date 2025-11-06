from heapq import heappop, heappush
from operator import sub
import random

def node(pos: tuple[int, int], g: int, h: int, parent: dict = None) -> dict:
    return {
        "g": g,
        "h": h,
        "f": g + h,
        "pos": pos,
        "parent": parent
    }
    

def heuristic(start, goal):
    return abs(goal[0] - start[0]) + abs(goal[1] - start[1])

def reconstruct_path(current):
    path = []
    
    while current is not None:
        path.append(current["pos"])
        current = current["parent"]

    return path[::-1]

def get_neighbors_pos(current, grid) -> list:
    x, y = current
    rows = len(grid)
    cols = len(grid[0])

    possible_moves = [
        (x + 1, y), (x - 1, y),
        (x, y + 1), (x, y - 1)
    ]

    return [
        (nx, ny) for nx, ny in possible_moves
        if 0 <= ny < rows and 0 <= nx < cols
        and grid[ny][nx] == 0
    ]

def astar(start: tuple[int, int], goal: tuple[int, int], grid):
    open_list: list[dict] = []
    open_dict = {}
    closed_list = set()

    start_node = node(start, 0, heuristic(start, goal))
    
    open_list.append((start_node["f"], start))
    open_dict[start_node["pos"]] = start_node

    while open_list != []:
        _, current_pos = heappop(open_list)
        current_node = open_dict[current_pos]

        if current_pos == goal:
            return reconstruct_path(current_node)
        
        closed_list.add(current_pos)

        for neighbor_pos in get_neighbors_pos(current_pos, grid):
            if neighbor_pos in closed_list:
                continue

            if grid[neighbor_pos[1]][neighbor_pos[0]] == 1:
                continue

            tentative_g = current_node["g"] + heuristic(neighbor_pos, goal)

            if neighbor_pos not in open_dict:
                neighbor = node(
                    neighbor_pos,
                    tentative_g,
                    heuristic(neighbor_pos, goal),
                    current_node
                )
                heappush(open_list, (neighbor["f"], neighbor_pos))
                open_dict[neighbor_pos] = neighbor

            elif tentative_g < open_dict[neighbor_pos]["g"]:
                neighbor = open_dict[neighbor_pos]
                neighbor["g"] = tentative_g
                neighbor["f"] = tentative_g + neighbor["h"]
                neighbor["parent"] = current_node

    return []


def generate_grid(width=20, height=10, obstacle_chance=0.2, start=None, goal=None):
    """
    Generate a 2D grid map with obstacles.
    
    Parameters:
        width, height: size of the grid
        obstacle_chance: probability of each cell being an obstacle (0 to 1)
        start, goal: optional (x, y) tuples for start and goal positions
    
    Returns:
        grid: list of lists containing 0 (free) and 1 (obstacle)
        start, goal: tuples with start/goal positions
    """
    # Initialize empty grid
    grid = [[0 for y in range(width)] for x in range(height)]

    # Randomly place obstacles
    for y in range(height):
        for x in range(width):
            if random.random() < obstacle_chance:
                grid[y][x] = 1  # obstacle

    # Choose random start/goal if not provided
    if start is None:
        start = (random.randint(0, width - 1), random.randint(0, height - 1))
    if goal is None:
        goal = (random.randint(0, width - 1), random.randint(0, height - 1))

    # Ensure start and goal are walkable
    grid[start[1]][start[0]] = 0
    grid[goal[1]][goal[0]] = 0

    return grid, start, goal


def print_grid(grid, start, goal, path = None):
    """
    Nicely print the grid with start and goal markers.
    """
    for y in range(len(grid)):
        row = ""
        for x in range(len(grid[0])):
            if (x, y) == start:
                row += "S "
            elif (x, y) == goal:
                row += "G "
            elif grid[y][x] == 1:
                row += "█ "
            elif path != None and (x, y) in path:
                row += "P "
            else:
                row += ". "
        print(row if row is not None else "")
    print()

def print_path_as_arrows(start, path):
    arrows = {
        (0, 1): "⇩",
        (0, -1): "⇧",
        (1, 0): "⇨",
        (-1, 0): "⇦"
    }
    path.pop(0)

    path_as_arrows = ""
    last_pos = path.pop(0)

    direction = tuple(map(sub, last_pos, start))
    path_as_arrows += arrows[direction] + " "
    
    for pos in path:
        direction = tuple(map(sub, pos, last_pos))
        path_as_arrows += arrows[direction] + " "
        last_pos = pos

    print(path_as_arrows, end="\n\n")

def do_grid(self, args):
    grid, start, goal = generate_grid(width=20, height=10, obstacle_chance=0.2)
    
    print_grid(grid, start, goal)
    print(f"Start: {start}, Goal: {goal}")
    
    path = astar(start, goal, grid)
    if path != []:
        print_grid(grid, start, goal, path)
        print("Path: ", end="")
        print_path_as_arrows(start, path)
    else:
        print("No path found")