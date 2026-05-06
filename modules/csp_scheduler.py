# ============================================================
# csp_scheduler.py
# Purpose : CSP Scheduler Module.
#           Assigns slots, rooms, and resources under
#           constraints. Runs only after Logic/KB confirms
#           eligibility. Finds conflict-free assignment
#           while respecting domains and constraints.
# Used by : main.py
# ============================================================

from data.encodings import VALID_SLOTS, SLOT_TIMES
from data.campus_graph import BOOKABLE_ROOMS


# ----------------------------------------------------------
# SIMULATED EXISTING BOOKINGS
# In a real system this would come from a database.
# Here we use a hardcoded dict to simulate conflicts.
# Format: { (room, slot): [list of booked names] }
# ----------------------------------------------------------
EXISTING_BOOKINGS = {
    ("AI_Lab",      1): ["DrKhan", "Sara"],
    ("AI_Lab",      2): ["Usman", "Zara"],
    ("AI_Lab",      3): [],
    ("AI_Lab",      4): ["DrSaad"],
    ("Library",     1): [],
    ("Library",     2): ["Ali"],
    ("Library",     3): [],
    ("Library",     4): [],
    ("Seminar_Room",1): ["DrAli"],
    ("Seminar_Room",2): [],
    ("Seminar_Room",3): ["DrKhan"],
    ("Seminar_Room",4): [],
    ("Exam_Hall",   1): [],
    ("Exam_Hall",   2): [],
    ("Exam_Hall",   3): ["Sara", "Usman"],
    ("Exam_Hall",   4): [],
    ("Science_Block",1): [],
    ("Science_Block",2): [],
    ("Science_Block",3): [],
    ("Science_Block",4): ["DrSaad"],
}

# max students per slot per room
MAX_CAPACITY = 10


# ----------------------------------------------------------
# HELPER: get_target_room
# Returns the correct room for a given category
# ----------------------------------------------------------
def get_target_room(category):
    """
    Maps service category to its appropriate campus room.
    Returns room name string.
    """
    category_room_map = {
        "AI_Lab_Support"  : "AI_Lab",
        "Viva_Scheduling" : "Seminar_Room",
        "Access_Request"  : "Library",
        "Maintenance"     : "Science_Block",
        "Emergency_Help"  : "AI_Lab",
    }
    return category_room_map.get(category, "AI_Lab")


# ----------------------------------------------------------
# HELPER: is_slot_available
# Checks if a room+slot combination is free
# ----------------------------------------------------------
def is_slot_available(room, slot, requester_name):
    """
    Checks if given room and slot is available.
    Constraints checked:
      1. Slot must be in valid range (1-4)
      2. Room must be bookable
      3. Slot must not be over capacity
      4. Same user must not already have that slot booked
    Returns (available, reason)
    """
    if slot not in VALID_SLOTS:
        return False, f"Slot {slot} is not valid."

    if room not in BOOKABLE_ROOMS:
        return False, f"Room '{room}' is not bookable."

    booked = EXISTING_BOOKINGS.get((room, slot), [])

    # check capacity
    if len(booked) >= MAX_CAPACITY:
        return False, f"Slot {slot} in {room} is fully booked."

    # check if same user already booked
    if requester_name in booked:
        return False, f"'{requester_name}' already has a booking in slot {slot}."

    return True, "Available"


# ----------------------------------------------------------
# FUNCTION: find_available_slot
# Tries preferred slot first, then searches for alternatives
# ----------------------------------------------------------
def find_available_slot(room, preferred_slot, name):
    """
    Tries to assign the preferred slot first.
    If preferred slot is not available, searches remaining
    slots in order and returns the first available one.
    Returns (slot, note) or (None, reason)
    """
    # try preferred slot first
    available, reason = is_slot_available(room, preferred_slot, name)
    if available:
        return preferred_slot, f"Preferred slot {preferred_slot} assigned."

    # preferred not available — try other slots
    tried_note = f"Slot {preferred_slot} unavailable ({reason})."
    for slot in VALID_SLOTS:
        if slot == preferred_slot:
            continue
        available, reason = is_slot_available(room, slot, name)
        if available:
            return slot, (
                f"{tried_note} "
                f"Slot {slot} is the next conflict-free assignment."
            )

    return None, f"{tried_note} No available slots found in {room}."


# ----------------------------------------------------------
# MAIN FUNCTION: run_csp
# Called by pipeline after Logic/KB confirms eligibility
# ----------------------------------------------------------
def run_csp(request_obj):
    """
    Main CSP function called by pipeline.
    Takes the request object, determines room, finds slot.
    Returns (success, csp_result_dict)
    
    Steps:
      1. Get target room from category
      2. Try preferred slot
      3. If not available, find next free slot
      4. Return assignment result
    """
    name           = request_obj.get("name", "")
    category       = request_obj.get("category", "")
    preferred_slot = request_obj.get("preferred_slot", 1)

    # if no preferred slot given, default to slot 1
    if preferred_slot is None:
        preferred_slot = 1

    # step 1: get target room for this category
    room = get_target_room(category)

    # step 2 & 3: find available slot
    assigned_slot, note = find_available_slot(room, preferred_slot, name)

    # step 4: return result
    if assigned_slot is None:
        return False, {
            "decision"      : "rejected",
            "assigned_room" : "",
            "assigned_slot" : None,
            "slot_time"     : "",
            "destination"   : "",
            "notes"         : note
        }

    slot_time = SLOT_TIMES.get(assigned_slot, "")

    return True, {
        "decision"      : "accepted",
        "assigned_room" : room,
        "assigned_slot" : assigned_slot,
        "slot_time"     : slot_time,
        "destination"   : room,
        "notes"         : note
    }