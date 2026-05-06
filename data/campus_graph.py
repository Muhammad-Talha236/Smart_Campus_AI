# ============================================================
# campus_graph.py
# Purpose : Defines the campus map as a graph.
#           Two versions are provided:
#           1. Unweighted graph — for BFS
#           2. Weighted graph   — for A* and UCS
#           Also stores node coordinates for A* heuristic
#           (straight-line / Manhattan distance estimate)
# Used by : search_navigation.py
# ============================================================


# ----------------------------------------------------------
# UNWEIGHTED CAMPUS GRAPH
# Each node connects to neighbors — no distances
# Used by BFS algorithm
# ----------------------------------------------------------
UNWEIGHTED_GRAPH = {
    "Main_Gate"       : ["Admin_Block", "Parking", "Bus_Stop"],
    "Bus_Stop"        : ["Main_Gate", "Medical_Center", "Hostel"],
    "Medical_Center"  : ["Bus_Stop", "Hostel", "Parking"],
    "Hostel"          : ["Bus_Stop", "Medical_Center", "Cafeteria"],
    "Parking"         : ["Main_Gate", "Medical_Center", "Admin_Block", "Science_Block"],
    "Admin_Block"     : ["Main_Gate", "Parking", "Student_Services"],
    "Student_Services": ["Admin_Block", "Exam_Hall", "Library"],
    "Exam_Hall"       : ["Student_Services", "Seminar_Room"],
    "Seminar_Room"    : ["Exam_Hall", "AI_Lab"],
    "Library"         : ["Student_Services", "Science_Block", "AI_Lab", "Seminar_Room"],
    "AI_Lab"          : ["Library", "Science_Block", "Seminar_Room"],
    "Science_Block"   : ["Parking", "Library", "AI_Lab", "Cafeteria"],
    "Cafeteria"       : ["Hostel", "Science_Block"]
}


# ----------------------------------------------------------
# WEIGHTED CAMPUS GRAPH
# Each edge has a cost (distance / travel time)
# Used by A* and UCS algorithms
# Format: { node: [(neighbor, cost), ...] }
# ----------------------------------------------------------
WEIGHTED_GRAPH = {
    "Main_Gate"       : [("Admin_Block", 4), ("Parking", 2),  ("Bus_Stop", 1)],
    "Bus_Stop"        : [("Main_Gate", 1),   ("Medical_Center", 2), ("Hostel", 2)],
    "Medical_Center"  : [("Bus_Stop", 2),    ("Hostel", 1),   ("Parking", 5)],
    "Hostel"          : [("Bus_Stop", 2),    ("Medical_Center", 1), ("Cafeteria", 3)],
    "Parking"         : [("Main_Gate", 2),   ("Medical_Center", 5), ("Admin_Block", 2), ("Science_Block", 3)],
    "Admin_Block"     : [("Main_Gate", 4),   ("Parking", 2),  ("Student_Services", 1)],
    "Student_Services": [("Admin_Block", 1), ("Exam_Hall", 2), ("Library", 2)],
    "Exam_Hall"       : [("Student_Services", 2), ("Seminar_Room", 1)],
    "Seminar_Room"    : [("Exam_Hall", 1),   ("AI_Lab", 2)],
    "Library"         : [("Student_Services", 2), ("Science_Block", 3), ("AI_Lab", 1), ("Seminar_Room", 2)],
    "AI_Lab"          : [("Library", 1),     ("Science_Block", 1), ("Seminar_Room", 2)],
    "Science_Block"   : [("Parking", 3),     ("Library", 3),  ("AI_Lab", 1), ("Cafeteria", 3)],
    "Cafeteria"       : [("Hostel", 3),      ("Science_Block", 3)]
}


# ----------------------------------------------------------
# NODE COORDINATES
# (x, y) grid coordinates for each campus location
# Used by A* heuristic (Manhattan distance estimate)
# These are taken from the project diagram
# ----------------------------------------------------------
NODE_COORDINATES = {
    "Main_Gate"       : (0, 4),
    "Bus_Stop"        : (0, 1),
    "Medical_Center"  : (1, 1),
    "Hostel"          : (2, 0),
    "Parking"         : (2, 4),
    "Admin_Block"     : (3, 5),
    "Student_Services": (6, 5),
    "Exam_Hall"       : (8, 5),
    "Seminar_Room"    : (10, 4),
    "Library"         : (6, 2),
    "AI_Lab"          : (9, 2),
    "Science_Block"   : (7, 1),
    "Cafeteria"       : (4, 1)
}


# ----------------------------------------------------------
# ALL VALID CAMPUS LOCATIONS
# Used by preprocessing for location validation
# ----------------------------------------------------------
VALID_LOCATIONS = list(NODE_COORDINATES.keys())


# ----------------------------------------------------------
# BOOKABLE ROOMS
# Only these rooms can be assigned by CSP scheduler
# ----------------------------------------------------------
BOOKABLE_ROOMS = [
    "AI_Lab",
    "Library",
    "Seminar_Room",
    "Exam_Hall",
    "Science_Block"
]


# ----------------------------------------------------------
# HEURISTIC FUNCTION FOR A*
# Manhattan distance between two nodes
# h(n) = |x1-x2| + |y1-y2|
# ----------------------------------------------------------
def heuristic(node, goal):
    """
    Calculates Manhattan distance between node and goal.
    Used as heuristic estimate in A* algorithm.
    Returns 0 if node coordinates are not found.
    """
    if node not in NODE_COORDINATES or goal not in NODE_COORDINATES:
        return 0
    x1, y1 = NODE_COORDINATES[node]
    x2, y2 = NODE_COORDINATES[goal]
    return abs(x1 - x2) + abs(y1 - y2)