# ============================================================
# knowledge_base.py
# Purpose : Stores all facts and rules for the Logic /
#           Knowledge Base module.
#           Facts  = things we know are true
#           Rules  = if condition then conclusion
# Used by : logic_kb.py
# ============================================================


# ----------------------------------------------------------
# FACTS
# These are known true statements about users and campus
# Format: set of strings representing true predicates
# ----------------------------------------------------------
FACTS = {
    # --- Teaching facts ---
    "Teaches(DrKhan, AI)",
    "Teaches(DrSaad, DataStructures)",
    "Teaches(DrAli, Networks)",

    # --- Student facts ---
    "Student(Ali)",
    "Student(Sara)",
    "Student(Usman)",
    "Student(Zara)",

    # --- Instructor facts ---
    "Instructor(DrKhan)",
    "Instructor(DrSaad)",
    "Instructor(DrAli)",

    # --- Staff facts ---
    "Staff(Ahmed)",
    "Staff(Bilal)",

    # --- Completed courses ---
    "Completed(Ali, ProgrammingFundamentals)",
    "Completed(Ali, DiscreteMath)",
    "Completed(Sara, ProgrammingFundamentals)",
    "Completed(Usman, ProgrammingFundamentals)",
    "Completed(Zara, ProgrammingFundamentals)",
    "Completed(Zara, DiscreteMath)",

    # --- Enrolled facts ---
    "Enrolled(Ali, AI)",
    "Enrolled(Sara, AI)",
    "Enrolled(Zara, AI)",

    # --- Lab access facts ---
    "HasLabAccess(DrKhan, AI_Lab)",
    "HasLabAccess(DrSaad, AI_Lab)",
    "HasLabAccess(Ahmed, AI_Lab)",

    # --- Registered for viva ---
    "RegisteredViva(Ali)",
    "RegisteredViva(Sara)",
    "RegisteredViva(Zara)"
}


# ----------------------------------------------------------
# RULES
# Format: list of (conditions_list, conclusion_string)
# conditions = facts that must ALL be true
# conclusion = new fact derived if conditions are true
# ----------------------------------------------------------
RULES = [

    # Rule 1: If x teaches AI then x is instructor of AI
    (
        ["Teaches({x}, AI)"],
        "InstructorOfAI({x})"
    ),

    # Rule 2: If x is instructor of AI then x can use Lab1
    (
        ["InstructorOfAI({x})"],
        "UsesLab({x}, Lab1)"
    ),

    # Rule 3: If x is enrolled in AI lab support eligible
    (
        ["Enrolled({x}, AI)"],
        "EligibleLabSupport({x})"
    ),

    # Rule 4: Student + completed PF = eligible for AI course
    (
        ["Student({x})", "Completed({x}, ProgrammingFundamentals)"],
        "Eligible({x}, AI)"
    ),

    # Rule 5: Eligible for AI = can request AI Lab Support
    (
        ["Eligible({x}, AI)"],
        "CanRequest({x}, AI_Lab_Support)"
    ),

    # Rule 6: Instructor can always request lab support
    (
        ["Instructor({x})"],
        "CanRequest({x}, AI_Lab_Support)"
    ),

    # Rule 7: Staff can request maintenance
    (
        ["Staff({x})"],
        "CanRequest({x}, Maintenance)"
    ),

    # Rule 8: Registered for viva can request viva scheduling
    (
        ["RegisteredViva({x})"],
        "CanRequest({x}, Viva_Scheduling)"
    ),

    # Rule 9: Student can request access request
    (
        ["Student({x})"],
        "CanRequest({x}, Access_Request)"
    ),

    # Rule 10: Anyone can request emergency help
    (
        ["Student({x})"],
        "CanRequest({x}, Emergency_Help)"
    ),
    (
        ["Instructor({x})"],
        "CanRequest({x}, Emergency_Help)"
    ),
    (
        ["Staff({x})"],
        "CanRequest({x}, Emergency_Help)"
    ),
]


# ----------------------------------------------------------
# ROLE PERMISSIONS
# Which roles can submit which request types
# ----------------------------------------------------------
ROLE_PERMISSIONS = {
    "student": [
        "Navigation_Only",
        "Eligibility_Check",
        "Booking_or_Scheduling",
        "Urgent_Service_Request",
        "Full_Service_Request"
    ],
    "instructor": [
        "Navigation_Only",
        "Eligibility_Check",
        "Booking_or_Scheduling",
        "Urgent_Service_Request",
        "Full_Service_Request"
    ],
    "staff": [
        "Navigation_Only",
        "Eligibility_Check",
        "Booking_or_Scheduling",
        "Urgent_Service_Request",
        "Full_Service_Request"
    ]
}


# ----------------------------------------------------------
# CATEGORY PERMISSIONS PER ROLE
# Which role can request which category
# ----------------------------------------------------------
CATEGORY_ROLE_MAP = {
    "AI_Lab_Support"  : ["student", "instructor"],
    "Viva_Scheduling" : ["student", "instructor"],
    "Access_Request"  : ["student", "instructor", "staff"],
    "Maintenance"     : ["staff", "instructor"],
    "Emergency_Help"  : ["student", "instructor", "staff"]
}