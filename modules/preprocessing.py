# ============================================================
# preprocessing.py
# Purpose : First module of the system.
#           Takes raw user input from CLI, validates all
#           fields, normalizes values to standard naming,
#           and builds one clean standard request object.
#           Also prepares flags for which modules will run.
# Used by : main.py, router.py
# ============================================================

import uuid
from data.encodings import (
    VALID_ROLES,
    VALID_REQUEST_TYPES,
    VALID_CATEGORIES,
    VALID_SLOTS,
    ROLE_ENCODING,
    REQUEST_TYPE_ENCODING
)
from data.campus_graph import VALID_LOCATIONS, NODE_COORDINATES, heuristic


# ----------------------------------------------------------
# NORMALIZATION MAPS
# Converts common user typos / lowercase into standard names
# ----------------------------------------------------------
LOCATION_NORMALIZE = {
    "main gate"        : "Main_Gate",
    "maingate"         : "Main_Gate",
    "bus stop"         : "Bus_Stop",
    "busstop"          : "Bus_Stop",
    "medical center"   : "Medical_Center",
    "medicalcenter"    : "Medical_Center",
    "medical"          : "Medical_Center",
    "hostel"           : "Hostel",
    "parking"          : "Parking",
    "admin block"      : "Admin_Block",
    "adminblock"       : "Admin_Block",
    "admin"            : "Admin_Block",
    "student services" : "Student_Services",
    "studentservices"  : "Student_Services",
    "student service"  : "Student_Services",
    "exam hall"        : "Exam_Hall",
    "examhall"         : "Exam_Hall",
    "exam"             : "Exam_Hall",
    "seminar room"     : "Seminar_Room",
    "seminarroom"      : "Seminar_Room",
    "seminar"          : "Seminar_Room",
    "library"          : "Library",
    "ai lab"           : "AI_Lab",
    "ailab"            : "AI_Lab",
    "ai_lab"           : "AI_Lab",
    "science block"    : "Science_Block",
    "scienceblock"     : "Science_Block",
    "science"          : "Science_Block",
    "cafeteria"        : "Cafeteria",
}

ROLE_NORMALIZE = {
    "student"    : "student",
    "instructor" : "instructor",
    "teacher"    : "instructor",
    "prof"       : "instructor",
    "professor"  : "instructor",
    "staff"      : "staff",
    "admin"      : "staff",
}

CATEGORY_NORMALIZE = {
    "ai lab support"   : "AI_Lab_Support",
    "ai_lab_support"   : "AI_Lab_Support",
    "ailabsupport"     : "AI_Lab_Support",
    "ai lab"           : "AI_Lab_Support",
    "viva scheduling"  : "Viva_Scheduling",
    "viva_scheduling"  : "Viva_Scheduling",
    "viva"             : "Viva_Scheduling",
    "access request"   : "Access_Request",
    "access_request"   : "Access_Request",
    "access"           : "Access_Request",
    "maintenance"      : "Maintenance",
    "emergency help"   : "Emergency_Help",
    "emergency_help"   : "Emergency_Help",
    "emergency"        : "Emergency_Help",
}


# ----------------------------------------------------------
# HELPER: normalize_location
# Converts user typed location to standard campus name
# ----------------------------------------------------------
def normalize_location(raw):
    """
    Takes raw location string from user.
    Converts to lowercase, strips spaces, then maps
    to standard campus location name.
    Returns None if location is not recognized.
    """
    if raw is None or raw.strip() == "":
        return None
    cleaned = raw.strip().lower()
    # direct match in normalize map
    if cleaned in LOCATION_NORMALIZE:
        return LOCATION_NORMALIZE[cleaned]
    # check if already a valid location (case insensitive)
    for loc in VALID_LOCATIONS:
        if loc.lower() == cleaned:
            return loc
    return None


# ----------------------------------------------------------
# HELPER: normalize_role
# Converts user typed role to standard role name
# ----------------------------------------------------------
def normalize_role(raw):
    """
    Takes raw role string from user.
    Maps to standard role name (student/instructor/staff).
    Returns None if not recognized.
    """
    if raw is None or raw.strip() == "":
        return None
    cleaned = raw.strip().lower()
    if cleaned in ROLE_NORMALIZE:
        return ROLE_NORMALIZE[cleaned]
    return None


# ----------------------------------------------------------
# HELPER: normalize_category
# Converts user typed category to standard category name
# ----------------------------------------------------------
def normalize_category(raw):
    """
    Takes raw category string from user.
    Maps to standard category name.
    Returns None if not recognized.
    """
    if raw is None or raw.strip() == "":
        return None
    cleaned = raw.strip().lower()
    if cleaned in CATEGORY_NORMALIZE:
        return CATEGORY_NORMALIZE[cleaned]
    # check if already matches a valid category
    for cat in VALID_CATEGORIES:
        if cat.lower() == cleaned:
            return cat
    return None


# ----------------------------------------------------------
# HELPER: generate_request_id
# Generates a unique request ID for each request
# ----------------------------------------------------------
def generate_request_id():
    """
    Generates a short unique request ID.
    Format: REQ-XXXX (4 digit random)
    """
    short = str(uuid.uuid4().int)[:4]
    return "REQ-" + short


# ----------------------------------------------------------
# HELPER: calculate_distance
# Calculates hop distance from current_location to AI_Lab
# Used as ANN feature (Distance field)
# ----------------------------------------------------------
def calculate_distance(current_location, destination="AI_Lab"):
    """
    Uses Manhattan distance heuristic between two locations.
    This gives an estimate of how far the user is.
    Returns 0 if location not found.
    """
    return heuristic(current_location, destination)


# ----------------------------------------------------------
# MAIN FUNCTION: preprocess_request
# Takes raw input dict, validates, normalizes, builds object
# ----------------------------------------------------------
def preprocess_request(raw_input):
    """
    Main preprocessing function.
    Input  : raw_input (dict) — raw fields from CLI
    Output : (success, result)
             success = True  → result is clean request object
             success = False → result is error message string
    Steps:
        1. Validate required base fields
        2. Normalize values
        3. Validate conditional fields by request type
        4. Build standard request object
        5. Prepare module flags
    """

    errors = []

    # -------------------------------------------------------
    # STEP 1: Normalize base fields
    # -------------------------------------------------------
    name = raw_input.get("name", "").strip()
    if not name:
        errors.append("Name is required.")

    role_raw = raw_input.get("role", "")
    role = normalize_role(role_raw)
    if role is None:
        errors.append(
            f"Invalid role '{role_raw}'. Valid: student, instructor, staff."
        )

    request_type = raw_input.get("request_type", "").strip()
    if request_type not in VALID_REQUEST_TYPES:
        errors.append(
            f"Invalid request type '{request_type}'."
        )

    # if base fields have errors, stop here
    if errors:
        return False, "\n".join(errors)

    # -------------------------------------------------------
    # STEP 2: Build base request object with defaults
    # -------------------------------------------------------
    request_obj = {
        "request_id"       : generate_request_id(),
        "name"             : name,
        "role"             : role,
        "request_type"     : request_type,
        "category"         : "",
        "current_location" : "",
        "destination"      : "",
        "preferred_slot"   : None,
        "severity"         : 0,
        "time_sensitivity" : 0,
        "crowd_level"      : 0,
        "group_id"         : "",
        "query"            : "",
        "eligibility_claim": False,
        "description_note" : "",
        "distance"         : 0,
        # module flags
        "needs_ann"        : False,
        "needs_logic"      : False,
        "needs_csp"        : False,
        "needs_search"     : False,
    }

    # -------------------------------------------------------
    # STEP 3: Validate & fill conditional fields
    # -------------------------------------------------------

    # --- Navigation_Only ---
    if request_type == "Navigation_Only":
        loc = normalize_location(raw_input.get("current_location", ""))
        dest = normalize_location(raw_input.get("destination", ""))
        if loc is None:
            errors.append("Invalid or missing current_location.")
        if dest is None:
            errors.append("Invalid or missing destination.")
        if loc and dest and loc == dest:
            errors.append("current_location and destination cannot be same.")
        if not errors:
            request_obj["current_location"] = loc
            request_obj["destination"]      = dest
            request_obj["needs_search"]     = True

    # --- Eligibility_Check ---
    elif request_type == "Eligibility_Check":
        query = raw_input.get("query", "").strip()
        if not query:
            errors.append("Query is required for Eligibility_Check.")
        else:
            request_obj["query"]       = query
            request_obj["needs_logic"] = True

    # --- Booking_or_Scheduling ---
    elif request_type == "Booking_or_Scheduling":
        cat = normalize_category(raw_input.get("category", ""))
        if cat is None:
            errors.append("Invalid or missing category.")

        slot = raw_input.get("preferred_slot", None)
        try:
            slot = int(slot)
            if slot not in VALID_SLOTS:
                errors.append("Slot must be between 1 and 4.")
        except (TypeError, ValueError):
            errors.append("Preferred slot must be a number (1-4).")
            slot = None

        loc = normalize_location(raw_input.get("current_location", ""))

        if not errors:
            request_obj["category"]        = cat
            request_obj["preferred_slot"]  = slot
            request_obj["needs_logic"]     = True
            request_obj["needs_csp"]       = True
            if loc:
                request_obj["current_location"] = loc
                request_obj["needs_search"]     = True
                request_obj["distance"]         = calculate_distance(loc)

    # --- Urgent_Service_Request ---
    elif request_type == "Urgent_Service_Request":
        cat = normalize_category(raw_input.get("category", ""))
        if cat is None:
            errors.append("Invalid or missing category.")

        loc = normalize_location(raw_input.get("current_location", ""))
        if loc is None:
            errors.append("Invalid or missing current_location.")

        severity = raw_input.get("severity", None)
        time_sens = raw_input.get("time_sensitivity", None)
        crowd = raw_input.get("crowd_level", None)

        try:
            severity = int(severity)
            if not (1 <= severity <= 10):
                errors.append("Severity must be between 1 and 10.")
        except (TypeError, ValueError):
            errors.append("Severity must be a number (1-10).")
            severity = 0

        try:
            time_sens = int(time_sens)
            if not (1 <= time_sens <= 10):
                errors.append("Time sensitivity must be between 1 and 10.")
        except (TypeError, ValueError):
            errors.append("Time sensitivity must be a number (1-10).")
            time_sens = 0

        try:
            crowd = int(crowd)
            if not (1 <= crowd <= 10):
                errors.append("Crowd level must be between 1 and 10.")
        except (TypeError, ValueError):
            errors.append("Crowd level must be a number (1-10).")
            crowd = 0

        slot = raw_input.get("preferred_slot", None)
        try:
            slot = int(slot)
            if slot not in VALID_SLOTS:
                errors.append("Slot must be between 1 and 4.")
        except (TypeError, ValueError):
            slot = None

        if not errors:
            dist = calculate_distance(loc)
            request_obj["category"]         = cat
            request_obj["current_location"] = loc
            request_obj["severity"]         = severity
            request_obj["time_sensitivity"] = time_sens
            request_obj["crowd_level"]      = crowd
            request_obj["preferred_slot"]   = slot
            request_obj["distance"]         = dist
            request_obj["needs_ann"]        = True
            request_obj["needs_logic"]      = True
            request_obj["needs_csp"]        = True
            request_obj["needs_search"]     = True

    # --- Full_Service_Request ---
    elif request_type == "Full_Service_Request":
        cat = normalize_category(raw_input.get("category", ""))
        if cat is None:
            errors.append("Invalid or missing category.")

        loc = normalize_location(raw_input.get("current_location", ""))
        if loc is None:
            errors.append("Invalid or missing current_location.")

        severity = raw_input.get("severity", None)
        time_sens = raw_input.get("time_sensitivity", None)
        crowd = raw_input.get("crowd_level", None)

        try:
            severity = int(severity)
            if not (1 <= severity <= 10):
                errors.append("Severity must be between 1 and 10.")
        except (TypeError, ValueError):
            errors.append("Severity must be a number (1-10).")
            severity = 0

        try:
            time_sens = int(time_sens)
            if not (1 <= time_sens <= 10):
                errors.append("Time sensitivity must be between 1 and 10.")
        except (TypeError, ValueError):
            errors.append("Time sensitivity must be a number (1-10).")
            time_sens = 0

        try:
            crowd = int(crowd)
            if not (1 <= crowd <= 10):
                errors.append("Crowd level must be between 1 and 10.")
        except (TypeError, ValueError):
            errors.append("Crowd level must be a number (1-10).")
            crowd = 0

        slot = raw_input.get("preferred_slot", None)
        try:
            slot = int(slot)
            if slot not in VALID_SLOTS:
                errors.append("Slot must be between 1 and 4.")
        except (TypeError, ValueError):
            errors.append("Preferred slot must be a number (1-4).")
            slot = None

        desc = raw_input.get("description_note", "").strip()

        if not errors:
            dist = calculate_distance(loc)
            request_obj["category"]          = cat
            request_obj["current_location"]  = loc
            request_obj["severity"]          = severity
            request_obj["time_sensitivity"]  = time_sens
            request_obj["crowd_level"]       = crowd
            request_obj["preferred_slot"]    = slot
            request_obj["description_note"]  = desc
            request_obj["distance"]          = dist
            request_obj["needs_ann"]         = True
            request_obj["needs_logic"]       = True
            request_obj["needs_csp"]         = True
            request_obj["needs_search"]      = True

    # -------------------------------------------------------
    # STEP 4: If any errors found, return failure
    # -------------------------------------------------------
    if errors:
        return False, "\n".join(errors)

    # -------------------------------------------------------
    # STEP 5: Prepare ANN feature vector if ANN is needed
    # -------------------------------------------------------
    if request_obj["needs_ann"]:
        role_enc    = ROLE_ENCODING.get(role, 0)
        cat_enc     = REQUEST_TYPE_ENCODING.get(request_obj["category"], 0)
        severity    = request_obj["severity"]
        time_sens   = request_obj["time_sensitivity"]
        crowd       = request_obj["crowd_level"]
        distance    = request_obj["distance"]
        eligibility = 1  # assume true initially, Logic/KB will verify

        request_obj["ann_features"] = [
            role_enc,
            cat_enc,
            severity,
            time_sens,
            crowd,
            distance,
            eligibility
        ]

    return True, request_obj