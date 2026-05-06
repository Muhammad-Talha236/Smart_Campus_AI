# ============================================================
# encodings.py
# Purpose : Stores all numeric encodings used by ANN module.
#           Role, RequestType, and Boolean values are converted
#           to numbers here so ANN can process them.
# Used by : ann_priority.py, preprocessing.py
# ============================================================

# Role encoding
# student=0, instructor=1, staff=2
ROLE_ENCODING = {
    "student"    : 0,
    "instructor" : 1,
    "staff"      : 2
}

# Request type / category encoding
# Used for ANN feature vector position 2
REQUEST_TYPE_ENCODING = {
    "AI_Lab_Support"  : 0,
    "Viva_Scheduling" : 1,
    "Access_Request"  : 2,
    "Maintenance"     : 3,
    "Emergency_Help"  : 4
}

# Valid roles accepted by system
VALID_ROLES = ["student", "instructor", "staff"]

# Valid request types accepted by system
VALID_REQUEST_TYPES = [
    "Navigation_Only",
    "Eligibility_Check",
    "Booking_or_Scheduling",
    "Urgent_Service_Request",
    "Full_Service_Request"
]

# Valid categories accepted by system
VALID_CATEGORIES = [
    "AI_Lab_Support",
    "Viva_Scheduling",
    "Access_Request",
    "Maintenance",
    "Emergency_Help"
]

# Valid slot numbers
VALID_SLOTS = [1, 2, 3, 4]

# Slot display names (for output display)
SLOT_TIMES = {
    1 : "08:00 AM - 09:30 AM",
    2 : "10:00 AM - 11:30 AM",
    3 : "12:00 PM - 01:30 PM",
    4 : "02:00 PM - 03:30 PM"
}

# ANN feature order — must not be changed
# This is the fixed order for feature vector
FEATURE_ORDER = [
    "Role",
    "RequestType",
    "Severity",
    "TimeSensitivity",
    "CrowdLevel",
    "Distance",
    "Eligibility"
]

# Priority labels used by MLP (multiclass)
PRIORITY_LABELS = {
    0 : "low",
    1 : "normal",
    2 : "high",
    3 : "urgent"
}

# Binary priority labels used by Perceptron
BINARY_LABELS = {
    0 : "not_urgent",
    1 : "urgent"
}