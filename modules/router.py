# ============================================================
# router.py
# Purpose : Request Router — control flow brain of the system.
#           Reads request_type from the clean request object
#           and decides which modules should run and in what
#           order. Does not solve anything itself.
# Used by : main.py
# ============================================================


# ----------------------------------------------------------
# PIPELINE DEFINITIONS
# Each request type maps to a fixed module sequence
# ----------------------------------------------------------
PIPELINES = {
    "Navigation_Only"       : ["Search"],
    "Eligibility_Check"     : ["Logic_KB"],
    "Booking_or_Scheduling" : ["Logic_KB", "CSP", "Search"],
    "Urgent_Service_Request": ["ANN", "Logic_KB", "CSP", "Search"],
    "Full_Service_Request"  : ["ANN", "Logic_KB", "CSP", "Search"],
}


# ----------------------------------------------------------
# MAIN FUNCTION: route_request
# Reads request object, returns routing decision
# ----------------------------------------------------------
def route_request(request_obj):
    """
    Takes the clean request object from preprocessing.
    Reads request_type field.
    Returns a routing control object with:
      - selected_pipeline : list of modules to run in order
      - needs_ann         : True/False
      - needs_logic       : True/False
      - needs_csp         : True/False
      - needs_search      : True/False
    Returns error if request_type is not recognized.
    """

    request_type = request_obj.get("request_type", "")
    request_id   = request_obj.get("request_id", "N/A")

    # check if request type is valid
    if request_type not in PIPELINES:
        return False, f"Unknown request type: '{request_type}'"

    # get pipeline for this request type
    pipeline = PIPELINES[request_type]

    # build routing control object
    routing = {
        "request_id"       : request_id,
        "request_type"     : request_type,
        "selected_pipeline": pipeline,
        "needs_ann"        : "ANN"      in pipeline,
        "needs_logic"      : "Logic_KB" in pipeline,
        "needs_csp"        : "CSP"      in pipeline,
        "needs_search"     : "Search"   in pipeline,
    }

    return True, routing


# ----------------------------------------------------------
# HELPER: print_routing_decision
# Displays routing decision clearly in CLI
# ----------------------------------------------------------
def print_routing_decision(routing):
    """
    Prints the routing decision to CLI in a readable format.
    Shows which pipeline was selected and which modules run.
    """
    print()
    print("=" * 50)
    print("  REQUEST ROUTER — PIPELINE SELECTED")
    print("=" * 50)
    print(f"  Request ID   : {routing['request_id']}")
    print(f"  Request Type : {routing['request_type']}")
    print(f"  Pipeline     : {' → '.join(routing['selected_pipeline'])}")
    print()
    print("  Module Flags:")
    print(f"    ANN        : {'YES' if routing['needs_ann']    else 'NO'}")
    print(f"    Logic / KB : {'YES' if routing['needs_logic']  else 'NO'}")
    print(f"    CSP        : {'YES' if routing['needs_csp']    else 'NO'}")
    print(f"    Search     : {'YES' if routing['needs_search'] else 'NO'}")
    print("=" * 50)