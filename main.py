# ============================================================
# main.py
# Purpose : Entry point of Smart Campus AI System.
#           Handles CLI interaction, collects user input,
#           calls preprocessing, then runs the correct
#           pipeline based on routing decision.
#           Displays final response to user.
# ============================================================

import sys
import os

# make sure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.preprocessing   import preprocess_request
from modules.router           import route_request, print_routing_decision
from modules.ann_priority     import run_ann
from modules.logic_kb         import run_logic
from modules.csp_scheduler    import run_csp
from modules.search_navigation import run_search
from modules.final_response   import build_final_response, display_final_response
from utils.display            import (
    print_banner, print_section_header,
    print_success, print_error, print_info,
    print_separator
)
from utils.validators         import (
    validate_name, validate_integer_field,
    validate_yes_no
)
from data.encodings import VALID_REQUEST_TYPES, VALID_CATEGORIES, SLOT_TIMES
from data.campus_graph import VALID_LOCATIONS


# ----------------------------------------------------------
# HELPER: get_input
# Wraps input() with a label and optional default
# ----------------------------------------------------------
def get_input(prompt, default=None):
    """
    Prompts user for input.
    If default is provided and user presses Enter, returns default.
    """
    if default:
        value = input(f"  {prompt} [{default}]: ").strip()
        return value if value else default
    else:
        return input(f"  {prompt}: ").strip()


# ----------------------------------------------------------
# HELPER: select_from_menu
# Displays numbered menu and returns selected key
# ----------------------------------------------------------
def select_from_menu(title, options):
    """
    Shows a numbered menu and returns the selected value.
    options = list of strings
    Returns the selected string value.
    """
    print()
    print(f"  {title}")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        choice = input("  Enter choice (number): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print_error(f"Please enter a number between 1 and {len(options)}.")
        except ValueError:
            print_error("Invalid input. Enter a number.")


# ----------------------------------------------------------
# INPUT COLLECTOR: collect_base_input
# Collects name, role, request_type
# ----------------------------------------------------------
def collect_base_input():
    """
    Collects the base fields common to all request types:
      - Name
      - Role
      - Request Type
    Returns raw_input dict with these fields.
    """
    raw = {}

    # name
    while True:
        name = get_input("Enter your Name")
        ok, msg = validate_name(name)
        if ok:
            raw["name"] = name
            break
        print_error(msg)

    # role
    raw["role"] = select_from_menu(
        "Select your Role:",
        ["student", "instructor", "staff"]
    )

    # request type
    raw["request_type"] = select_from_menu(
        "Select Request Type:",
        VALID_REQUEST_TYPES
    )

    return raw


# ----------------------------------------------------------
# INPUT COLLECTOR: collect_navigation_input
# ----------------------------------------------------------
def collect_navigation_input(raw):
    """
    Collects extra fields for Navigation_Only request.
    """
    print_section_header("Navigation Details")

    # show valid locations
    print_info("Valid locations: " + ", ".join(VALID_LOCATIONS))
    print()

    raw["current_location"] = get_input("Enter Current Location")
    raw["destination"]      = get_input("Enter Destination")
    return raw


# ----------------------------------------------------------
# INPUT COLLECTOR: collect_eligibility_input
# ----------------------------------------------------------
def collect_eligibility_input(raw):
    """
    Collects extra fields for Eligibility_Check request.
    """
    print_section_header("Eligibility Query")
    print_info("Example query: UsesLab(DrKhan, Lab1)")
    print_info("Example query: CanRequest(Ali, AI_Lab_Support)")
    print()
    raw["query"] = get_input("Enter Eligibility Query")
    return raw


# ----------------------------------------------------------
# INPUT COLLECTOR: collect_booking_input
# ----------------------------------------------------------
def collect_booking_input(raw):
    """
    Collects extra fields for Booking_or_Scheduling request.
    """
    print_section_header("Booking Details")

    raw["category"] = select_from_menu(
        "Select Service Category:",
        VALID_CATEGORIES
    )

    # preferred slot
    print()
    print_info("Available Slots:")
    for slot_num, slot_time in SLOT_TIMES.items():
        print(f"    Slot {slot_num}: {slot_time}")
    print()
    raw["preferred_slot"] = get_input("Enter Preferred Slot (1-4)")

    print_info("Valid locations: " + ", ".join(VALID_LOCATIONS))
    print()
    raw["current_location"] = get_input("Enter Current Location (optional, press Enter to skip)", "")

    return raw


# ----------------------------------------------------------
# INPUT COLLECTOR: collect_service_input
# Used for Urgent_Service_Request and Full_Service_Request
# ----------------------------------------------------------
def collect_service_input(raw):
    """
    Collects extra fields for Urgent and Full service requests.
    """
    print_section_header("Service Request Details")

    raw["category"] = select_from_menu(
        "Select Service Category:",
        VALID_CATEGORIES
    )

    print_info("Valid locations: " + ", ".join(VALID_LOCATIONS))
    print()
    raw["current_location"] = get_input("Enter Current Location")

    # preferred slot
    print()
    print_info("Available Slots:")
    for slot_num, slot_time in SLOT_TIMES.items():
        print(f"    Slot {slot_num}: {slot_time}")
    print()
    raw["preferred_slot"] = get_input("Enter Preferred Slot (1-4)")

    # severity
    print()
    print_info("Severity: How serious is your issue? (1=Minor, 10=Critical)")
    while True:
        val = get_input("Enter Severity (1-10)")
        ok, result = validate_integer_field("Severity", val, 1, 10)
        if ok:
            raw["severity"] = result
            break
        print_error(result)

    # time sensitivity
    print_info("Time Sensitivity: How urgently do you need help? (1=No rush, 10=Immediately)")
    while True:
        val = get_input("Enter Time Sensitivity (1-10)")
        ok, result = validate_integer_field("Time Sensitivity", val, 1, 10)
        if ok:
            raw["time_sensitivity"] = result
            break
        print_error(result)

    # crowd level
    print_info("Crowd Level: How busy is your current area? (1=Empty, 10=Very crowded)")
    while True:
        val = get_input("Enter Crowd Level (1-10)")
        ok, result = validate_integer_field("Crowd Level", val, 1, 10)
        if ok:
            raw["crowd_level"] = result
            break
        print_error(result)

    # description (optional for Full_Service only)
    if raw.get("request_type") == "Full_Service_Request":
        print()
        raw["description_note"] = get_input(
            "Enter Description / Note (optional, press Enter to skip)", ""
        )

    return raw


# ----------------------------------------------------------
# MAIN PIPELINE RUNNER
# Calls modules in correct order based on routing
# ----------------------------------------------------------
def run_pipeline(request_obj, routing):
    """
    Executes the pipeline for this request.
    Calls modules in the order defined by routing.
    Returns final response dict.
    """
    ann_result    = None
    logic_result  = None
    csp_result    = None
    search_result = None

    pipeline = routing["selected_pipeline"]
    print()
    print_info(f"Running pipeline: {' → '.join(pipeline)}")
    print()

    # --- ANN Module ---
    if routing["needs_ann"]:
        print_section_header("ANN Priority Prediction")
        success, ann_result = run_ann(request_obj)
        if not success:
            print_error(f"ANN Error: {ann_result.get('error','')}")
            return build_final_response(
                request_obj, rejected=True,
                reject_reason="ANN module failed."
            )
        print_success(
            f"Priority → Binary: {ann_result['binary_priority'].upper()} | "
            f"Final: {ann_result['final_priority'].upper()} | "
            f"Confidence: {ann_result['confidence']}"
        )

    # --- Logic/KB Module ---
    if routing["needs_logic"]:
        print_section_header("Logic / Knowledge Base Check")
        success, logic_result = run_logic(request_obj)

        if not success:
            print_error(f"Logic Error: {logic_result.get('explanation','')}")
            return build_final_response(
                request_obj, rejected=True,
                reject_reason="Logic/KB module error."
            )

        # For eligibility check — just return here
        if request_obj["request_type"] == "Eligibility_Check":
            entailed = logic_result.get("entailed", False)
            if entailed:
                print_success(f"Entailed: TRUE")
            else:
                print_error(f"Entailed: FALSE")
            print_info(logic_result.get("explanation", ""))
            return build_final_response(
                request_obj,
                logic_result=logic_result
            )

        # For service requests — check if allowed
        allowed = logic_result.get("allowed", False)
        if allowed:
            print_success(f"Eligibility: ALLOWED — {logic_result.get('explanation','')}")
        else:
            print_error(f"Eligibility: DENIED — {logic_result.get('explanation','')}")
            return build_final_response(
                request_obj,
                ann_result=ann_result,
                logic_result=logic_result,
                rejected=True,
                reject_reason=logic_result.get("explanation", "Not eligible.")
            )

    # --- CSP Scheduler ---
    if routing["needs_csp"]:
        print_section_header("CSP Slot / Room Assignment")
        success, csp_result = run_csp(request_obj)
        if not success or csp_result.get("decision") == "rejected":
            print_error(f"CSP: No slot available — {csp_result.get('notes','')}")
            return build_final_response(
                request_obj,
                ann_result=ann_result,
                logic_result=logic_result,
                csp_result=csp_result,
                rejected=True,
                reject_reason=csp_result.get("notes", "No slot available.")
            )
        room = csp_result.get("assigned_room", "")
        slot = csp_result.get("assigned_slot", "")
        time = csp_result.get("slot_time", "")
        print_success(f"Assigned: {room} | Slot {slot} ({time})")
        print_info(f"Note: {csp_result.get('notes','')}")

        # update destination in request_obj for search
        request_obj["destination"] = csp_result.get("destination", "")

    # --- Search / Navigation ---
    if routing["needs_search"]:
        source = request_obj.get("current_location", "")
        dest   = request_obj.get("destination", "")

        if source and dest and source != dest:
            print_section_header("Route Calculation (A*)")
            success, search_result = run_search(
                source, dest,
                graph_type="weighted",
                mode="operational"
            )
            if not success:
                print_error(f"Search: {search_result}")
                search_result = None
            else:
                path_str = " → ".join(search_result.get("path", []))
                print_success(
                    f"Algorithm: {search_result['algorithm_used']} | "
                    f"Path: {path_str} | "
                    f"Cost: {search_result['cost']}"
                )
        else:
            print_info("Navigation skipped (no valid source/destination).")
            search_result = None

    # build and return final response
    return build_final_response(
        request_obj,
        ann_result    = ann_result,
        logic_result  = logic_result,
        csp_result    = csp_result,
        search_result = search_result
    )


# ----------------------------------------------------------
# COMPARISON MODE
# Runs all search algorithms and shows comparison table
# ----------------------------------------------------------
def run_comparison_mode():
    """
    Special mode: runs all search algorithms on a route
    and displays a comparison table.
    """
    print_banner()
    print_section_header("Algorithm Comparison Mode")
    print_info("Valid locations: " + ", ".join(VALID_LOCATIONS))
    print()

    source = get_input("Enter Source Location")
    dest   = get_input("Enter Destination Location")

    print()
    print_info("Running all algorithms...")
    print()

    success, results = run_search(source, dest, mode="comparison")

    if not success:
        print_error(str(results))
        return

    # print comparison table
    print_separator("=", 70)
    print("  ALGORITHM COMPARISON TABLE")
    print_separator("=", 70)
    header = f"  {'Algorithm':<22} {'Cost':>6}  {'Steps':>6}  {'Expanded':>8}  Path"
    print(header)
    print_separator("-", 70)

    algo_order = ["BFS", "DFS", "IDS", "Bidirectional_BFS",
                  "UCS", "Greedy", "A*", "RBFS"]

    for algo in algo_order:
        if algo not in results:
            continue
        r = results[algo]
        path = r.get("path")
        if path:
            path_str = " → ".join(path[:4])
            if len(path) > 4:
                path_str += f" ... ({len(path)} nodes)"
            cost  = r.get("cost", 0)
            steps = r.get("steps", 0)
            exp   = r.get("nodes_expanded", 0)
        else:
            path_str = "No path found"
            cost = steps = exp = 0
        print(f"  {algo:<22} {cost:>6}  {steps:>6}  {exp:>8}  {path_str}")

    print_separator("=", 70)


# ----------------------------------------------------------
# MAIN FUNCTION
# ----------------------------------------------------------
def main():
    """
    Main function — program entry point.
    Shows banner, collects input, runs pipeline, displays result.
    """
    print_banner()

    while True:
        print()
        print("  OPTIONS:")
        print("    1. Submit a Request")
        print("    2. Algorithm Comparison Mode")
        print("    3. Exit")
        print()
        choice = get_input("Enter choice (1/2/3)")

        if choice == "3":
            print()
            print_info("Thank you for using Smart Campus AI System. Goodbye!")
            break

        elif choice == "2":
            run_comparison_mode()
            continue

        elif choice != "1":
            print_error("Invalid choice. Enter 1, 2, or 3.")
            continue

        # -------------------------------------------------------
        # STEP 1: Collect base input
        # -------------------------------------------------------
        print()
        print_section_header("User Information")
        raw_input = collect_base_input()

        request_type = raw_input.get("request_type", "")

        # -------------------------------------------------------
        # STEP 2: Collect fields based on request type
        # -------------------------------------------------------
        if request_type == "Navigation_Only":
            raw_input = collect_navigation_input(raw_input)

        elif request_type == "Eligibility_Check":
            raw_input = collect_eligibility_input(raw_input)

        elif request_type == "Booking_or_Scheduling":
            raw_input = collect_booking_input(raw_input)

        elif request_type in ["Urgent_Service_Request", "Full_Service_Request"]:
            raw_input = collect_service_input(raw_input)

        # -------------------------------------------------------
        # STEP 3: Preprocessing
        # -------------------------------------------------------
        print()
        print_section_header("Preprocessing & Validation")
        success, result = preprocess_request(raw_input)

        if not success:
            print_error("Input validation failed:")
            print_error(result)
            print()
            ok, _ = validate_yes_no(get_input("Try again? (yes/no)", "yes"))
            if ok:
                continue
            else:
                break

        request_obj = result
        print_success(
            f"Request ID: {request_obj['request_id']} | "
            f"User: {request_obj['name']} ({request_obj['role']})"
        )

        # -------------------------------------------------------
        # STEP 4: Routing
        # -------------------------------------------------------
        success, routing = route_request(request_obj)
        if not success:
            print_error(f"Routing failed: {routing}")
            continue

        print_routing_decision(routing)

        # -------------------------------------------------------
        # STEP 5: Run pipeline
        # -------------------------------------------------------
        final_response = run_pipeline(request_obj, routing)

        # -------------------------------------------------------
        # STEP 6: Display final response
        # -------------------------------------------------------
        display_final_response(final_response)

        # ask if user wants to submit another request
        print()
        answer = get_input("Submit another request? (yes/no)", "no")
        ok, _ = validate_yes_no(answer)
        if not ok:
            print()
            print_info("Thank you for using Smart Campus AI System. Goodbye!")
            break


# ----------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------
if __name__ == "__main__":
    main()