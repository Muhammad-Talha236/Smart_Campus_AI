# ============================================================
# search_navigation.py
# Purpose : Search & Navigation Module.
#           Computes campus routes using multiple algorithms.
#           Operational algorithms: BFS, A*, UCS
#           Comparison algorithms : DFS, DLS, IDS,
#                                   Bidirectional BFS,
#                                   Greedy Best-First, RBFS
#           Graph type decides which algorithm runs finally.
# Used by : main.py
# ============================================================

import heapq
from collections import deque
from data.campus_graph import (
    WEIGHTED_GRAPH,
    UNWEIGHTED_GRAPH,
    heuristic,
    VALID_LOCATIONS
)


# ----------------------------------------------------------
# HELPER: reconstruct_path
# Traces back from goal to start using parent map
# ----------------------------------------------------------
def reconstruct_path(parent, start, goal):
    """
    Traces back from goal node to start node
    using the parent dictionary built during search.
    Returns path as list from start to goal.
    """
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


# ----------------------------------------------------------
# ALGORITHM 1: BFS — Breadth First Search
# For UNWEIGHTED graph — gives shortest hop path
# ----------------------------------------------------------
def bfs(start, goal):
    """
    Breadth First Search on unweighted campus graph.
    Explores neighbors level by level.
    Guarantees shortest path in terms of hops (edges).
    Returns: path list, steps count, nodes expanded
    """
    if start not in UNWEIGHTED_GRAPH or goal not in UNWEIGHTED_GRAPH:
        return None, 0, 0

    visited  = set()
    queue    = deque([[start]])
    expanded = 0

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node in visited:
            continue
        visited.add(node)
        expanded += 1

        if node == goal:
            return path, len(path) - 1, expanded

        for neighbor in UNWEIGHTED_GRAPH.get(node, []):
            if neighbor not in visited:
                queue.append(path + [neighbor])

    return None, 0, expanded


# ----------------------------------------------------------
# ALGORITHM 2: DFS — Depth First Search
# Comparison algorithm — not guaranteed shortest path
# ----------------------------------------------------------
def dfs(start, goal):
    """
    Depth First Search on unweighted campus graph.
    Explores as deep as possible before backtracking.
    Not guaranteed to give shortest path.
    Returns: path list, steps count, nodes expanded
    """
    if start not in UNWEIGHTED_GRAPH or goal not in UNWEIGHTED_GRAPH:
        return None, 0, 0

    visited  = set()
    stack    = [[start]]
    expanded = 0

    while stack:
        path = stack.pop()
        node = path[-1]

        if node in visited:
            continue
        visited.add(node)
        expanded += 1

        if node == goal:
            return path, len(path) - 1, expanded

        for neighbor in reversed(UNWEIGHTED_GRAPH.get(node, [])):
            if neighbor not in visited:
                stack.append(path + [neighbor])

    return None, 0, expanded


# ----------------------------------------------------------
# ALGORITHM 3: DLS — Depth Limited Search
# Comparison algorithm — DFS with a depth limit
# ----------------------------------------------------------
def dls(start, goal, limit):
    """
    Depth Limited Search — DFS with maximum depth limit.
    Will not explore nodes beyond given depth limit.
    Returns: path list, steps count, nodes expanded
    """
    def dls_recursive(path, node, limit, visited, expanded):
        if node == goal:
            return path, expanded
        if limit == 0:
            return None, expanded
        visited.add(node)
        expanded[0] += 1
        for neighbor in UNWEIGHTED_GRAPH.get(node, []):
            if neighbor not in visited:
                result, expanded = dls_recursive(
                    path + [neighbor], neighbor,
                    limit - 1, visited, expanded
                )
                if result is not None:
                    return result, expanded
        visited.discard(node)
        return None, expanded

    if start not in UNWEIGHTED_GRAPH or goal not in UNWEIGHTED_GRAPH:
        return None, 0, 0

    expanded = [0]
    result, expanded = dls_recursive([start], start, limit, set(), expanded)
    if result:
        return result, len(result) - 1, expanded[0]
    return None, 0, expanded[0]


# ----------------------------------------------------------
# ALGORITHM 4: IDS — Iterative Deepening Search
# Comparison algorithm — repeated DLS with increasing depth
# ----------------------------------------------------------
def ids(start, goal, max_depth=20):
    """
    Iterative Deepening Search.
    Runs DLS repeatedly with increasing depth limits.
    Combines benefits of BFS (optimal) and DFS (memory).
    Returns: path list, steps count, nodes expanded
    """
    if start not in UNWEIGHTED_GRAPH or goal not in UNWEIGHTED_GRAPH:
        return None, 0, 0

    total_expanded = 0
    for depth in range(max_depth + 1):
        path, steps, expanded = dls(start, goal, depth)
        total_expanded += expanded
        if path is not None:
            return path, steps, total_expanded

    return None, 0, total_expanded


# ----------------------------------------------------------
# ALGORITHM 5: UCS — Uniform Cost Search
# For WEIGHTED graph — gives least cost path (no heuristic)
# ----------------------------------------------------------
def ucs(start, goal):
    """
    Uniform Cost Search on weighted campus graph.
    Always expands the node with lowest cumulative cost.
    Guarantees optimal (least cost) path.
    Returns: path list, total cost, steps, nodes expanded
    """
    if start not in WEIGHTED_GRAPH or goal not in WEIGHTED_GRAPH:
        return None, 0, 0, 0

    # priority queue: (cost, node, path)
    pq       = [(0, start, [start])]
    visited  = {}
    expanded = 0

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited and visited[node] <= cost:
            continue
        visited[node] = cost
        expanded += 1

        if node == goal:
            return path, cost, len(path) - 1, expanded

        for neighbor, edge_cost in WEIGHTED_GRAPH.get(node, []):
            new_cost = cost + edge_cost
            if neighbor not in visited or visited[neighbor] > new_cost:
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    return None, 0, 0, expanded


# ----------------------------------------------------------
# ALGORITHM 6: Greedy Best-First Search
# Comparison algorithm — uses only heuristic, not cost
# ----------------------------------------------------------
def greedy_best_first(start, goal):
    """
    Greedy Best-First Search on weighted campus graph.
    Always expands node closest to goal by heuristic.
    Not guaranteed to give optimal path.
    Returns: path list, total cost, steps, nodes expanded
    """
    if start not in WEIGHTED_GRAPH or goal not in WEIGHTED_GRAPH:
        return None, 0, 0, 0

    # priority queue: (heuristic, node, cost, path)
    pq       = [(heuristic(start, goal), start, 0, [start])]
    visited  = set()
    expanded = 0

    while pq:
        h, node, cost, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)
        expanded += 1

        if node == goal:
            return path, cost, len(path) - 1, expanded

        for neighbor, edge_cost in WEIGHTED_GRAPH.get(node, []):
            if neighbor not in visited:
                heapq.heappush(pq, (
                    heuristic(neighbor, goal),
                    neighbor,
                    cost + edge_cost,
                    path + [neighbor]
                ))

    return None, 0, 0, expanded


# ----------------------------------------------------------
# ALGORITHM 7: A* Search
# MAIN algorithm for WEIGHTED graph with heuristic
# f(n) = g(n) + h(n)
# ----------------------------------------------------------
def astar(start, goal):
    """
    A* Search on weighted campus graph.
    Combines actual cost g(n) and heuristic h(n).
    f(n) = g(n) + h(n)
    Guarantees optimal path when heuristic is admissible.
    Returns: path list, total cost, steps, nodes expanded
    """
    if start not in WEIGHTED_GRAPH or goal not in WEIGHTED_GRAPH:
        return None, 0, 0, 0

    # priority queue: (f_cost, g_cost, node, path)
    start_h = heuristic(start, goal)
    pq      = [(start_h, 0, start, [start])]
    visited = {}
    expanded = 0

    while pq:
        f, g, node, path = heapq.heappop(pq)

        if node in visited and visited[node] <= g:
            continue
        visited[node] = g
        expanded += 1

        if node == goal:
            return path, g, len(path) - 1, expanded

        for neighbor, edge_cost in WEIGHTED_GRAPH.get(node, []):
            new_g = g + edge_cost
            new_h = heuristic(neighbor, goal)
            new_f = new_g + new_h
            if neighbor not in visited or visited[neighbor] > new_g:
                heapq.heappush(pq, (new_f, new_g, neighbor, path + [neighbor]))

    return None, 0, 0, expanded


# ----------------------------------------------------------
# ALGORITHM 8: Bidirectional BFS
# Comparison algorithm — searches from both ends
# ----------------------------------------------------------
def bidirectional_bfs(start, goal):
    """
    Bidirectional BFS on unweighted campus graph.
    Searches simultaneously from start and goal.
    Meets in the middle — faster than normal BFS.
    Returns: path list, steps count, nodes expanded
    """
    if start not in UNWEIGHTED_GRAPH or goal not in UNWEIGHTED_GRAPH:
        return None, 0, 0

    if start == goal:
        return [start], 0, 1

    # forward and backward frontiers
    front_visited = {start: [start]}
    back_visited  = {goal:  [goal]}
    front_queue   = deque([start])
    back_queue    = deque([goal])
    expanded      = 0

    while front_queue and back_queue:
        # expand forward
        node = front_queue.popleft()
        expanded += 1
        for neighbor in UNWEIGHTED_GRAPH.get(node, []):
            if neighbor not in front_visited:
                front_visited[neighbor] = front_visited[node] + [neighbor]
                front_queue.append(neighbor)
            if neighbor in back_visited:
                # paths met
                full_path = (front_visited[neighbor] +
                             list(reversed(back_visited[neighbor]))[1:])
                return full_path, len(full_path) - 1, expanded

        # expand backward
        node = back_queue.popleft()
        expanded += 1
        for neighbor in UNWEIGHTED_GRAPH.get(node, []):
            if neighbor not in back_visited:
                back_visited[neighbor] = back_visited[node] + [neighbor]
                back_queue.append(neighbor)
            if neighbor in front_visited:
                full_path = (front_visited[neighbor] +
                             list(reversed(back_visited[neighbor]))[1:])
                return full_path, len(full_path) - 1, expanded

    return None, 0, expanded


# ----------------------------------------------------------
# ALGORITHM 9: RBFS — Recursive Best First Search
# Comparison algorithm — memory efficient A* variant
# ----------------------------------------------------------
def rbfs(start, goal):
    """
    Recursive Best-First Search.
    Memory efficient version of A*.
    Uses recursion and tracks f-limit for backtracking.
    Returns: path list, total cost, steps, nodes expanded
    """
    expanded = [0]

    def rbfs_inner(node, path, g, f_limit):
        if node == goal:
            return path, g, f_limit

        successors = []
        for neighbor, cost in WEIGHTED_GRAPH.get(node, []):
            if neighbor not in path:
                new_g = g + cost
                new_f = new_g + heuristic(neighbor, goal)
                successors.append((new_f, new_g, neighbor, path + [neighbor]))

        if not successors:
            return None, g, float('inf')

        successors.sort(key=lambda x: x[0])

        while True:
            best_f, best_g, best_node, best_path = successors[0]

            if best_f > f_limit:
                return None, best_g, best_f

            if len(successors) > 1:
                alt_f = successors[1][0]
            else:
                alt_f = float('inf')

            expanded[0] += 1
            result, res_g, new_f = rbfs_inner(
                best_node, best_path, best_g, min(f_limit, alt_f)
            )
            successors[0] = (new_f, best_g, best_node, best_path)
            successors.sort(key=lambda x: x[0])

            if result is not None:
                return result, res_g, new_f

    if start not in WEIGHTED_GRAPH or goal not in WEIGHTED_GRAPH:
        return None, 0, 0, 0

    start_f = heuristic(start, goal)
    result, cost, _ = rbfs_inner(start, [start], 0, float('inf'))

    if result:
        return result, cost, len(result) - 1, expanded[0]
    return None, 0, 0, expanded[0]


# ----------------------------------------------------------
# MAIN FUNCTION: run_search
# Selects correct algorithm based on graph type + policy
# ----------------------------------------------------------
def run_search(source, destination, graph_type="weighted", mode="operational"):
    """
    Main search function called by pipeline.
    Selects algorithm based on:
      graph_type = 'weighted' or 'unweighted'
      mode       = 'operational' or 'comparison'

    Operational mode → returns one best result
    Comparison mode  → returns all algorithm results

    Returns: (success, result_dict)
    """
    # validate locations
    if source not in VALID_LOCATIONS:
        return False, f"Invalid source location: '{source}'"
    if destination not in VALID_LOCATIONS:
        return False, f"Invalid destination location: '{destination}'"
    if source == destination:
        return False, "Source and destination cannot be the same."

    # -------------------------------------------------------
    # OPERATIONAL MODE — one algorithm, one result
    # -------------------------------------------------------
    if mode == "operational":
        if graph_type == "unweighted":
            # BFS for unweighted
            path, steps, expanded = bfs(source, destination)
            if path is None:
                return False, "No route found between given locations."
            return True, {
                "algorithm_used" : "BFS",
                "graph_type"     : "unweighted",
                "path"           : path,
                "cost"           : steps,
                "steps"          : steps,
                "nodes_expanded" : expanded
            }
        else:
            # A* for weighted (primary)
            path, cost, steps, expanded = astar(source, destination)
            if path is None:
                # fallback to UCS
                path, cost, steps, expanded = ucs(source, destination)
                algo = "UCS"
            else:
                algo = "A*"
            if path is None:
                return False, "No route found between given locations."
            return True, {
                "algorithm_used" : algo,
                "graph_type"     : "weighted",
                "path"           : path,
                "cost"           : cost,
                "steps"          : steps,
                "nodes_expanded" : expanded
            }

    # -------------------------------------------------------
    # COMPARISON MODE — all algorithms, compare results
    # -------------------------------------------------------
    elif mode == "comparison":
        results = {}

        # unweighted algorithms
        p, s, e = bfs(source, destination)
        results["BFS"] = {
            "path": p, "cost": s, "steps": s, "nodes_expanded": e
        }

        p, s, e = dfs(source, destination)
        results["DFS"] = {
            "path": p, "cost": s, "steps": s, "nodes_expanded": e
        }

        p, s, e = ids(source, destination)
        results["IDS"] = {
            "path": p, "cost": s, "steps": s, "nodes_expanded": e
        }

        p, s, e = bidirectional_bfs(source, destination)
        results["Bidirectional_BFS"] = {
            "path": p, "cost": s, "steps": s, "nodes_expanded": e
        }

        # weighted algorithms
        p, c, s, e = ucs(source, destination)
        results["UCS"] = {
            "path": p, "cost": c, "steps": s, "nodes_expanded": e
        }

        p, c, s, e = greedy_best_first(source, destination)
        results["Greedy"] = {
            "path": p, "cost": c, "steps": s, "nodes_expanded": e
        }

        p, c, s, e = astar(source, destination)
        results["A*"] = {
            "path": p, "cost": c, "steps": s, "nodes_expanded": e
        }

        p, c, s, e = rbfs(source, destination)
        results["RBFS"] = {
            "path": p, "cost": c, "steps": s, "nodes_expanded": e
        }

        return True, results

    return False, "Invalid mode. Use 'operational' or 'comparison'."