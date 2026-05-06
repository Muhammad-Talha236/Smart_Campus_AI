# ============================================================
# final_response.py
# Purpose : Final Response Layer.
#           Collects outputs from all executed modules and
#           presents one coherent answer to the user.
# Used by : main.py
# ============================================================

from data.encodings import SLOT_TIMES


def build_final_response(request_obj, ann_result=None,
                          logic_result=None, csp_result=None,
                          search_result=None, rejected=False,
                          reject_reason=""):
    """
    Builds the final response dictionary from module outputs.
    Only includes fields from modules that actually ran.
    """
    request_id   = request_obj.get("request_id", "N/A")
    request_type = request_obj.get("request_type", "")

    response = {
        "request_id"  : request_id,
        "decision"    : "",
        "priority"    : {},
        "eligibility" : {},
        "assignment"  : {},
        "route"       : {},
        "message"     : ""
    }

    # --- REJECTED ---
    if rejected:
        response["decision"] = "rejected"
        response["message"]  = f"Request rejected: {reject_reason}"
        return response

    # --- PRIORITY (ANN) ---
    if ann_result:
        response["priority"] = {
            "binary_priority" : ann_result.get("binary_priority", ""),
            "final_priority"  : ann_result.get("final_priority", ""),
            "confidence"      : ann_result.get("confidence", 0.0)
        }

    # --- ELIGIBILITY (Logic/KB) ---
    if logic_result:
        if request_type == "Eligibility_Check":
            response["eligibility"] = {
                "entailed"    : logic_result.get("entailed", False),
                "explanation" : logic_result.get("explanation", "")
            }
            response["decision"] = "answered"
            response["message"]  = "Eligibility query answered successfully."
            return response
        else:
            response["eligibility"] = {
                "allowed"     : logic_result.get("allowed", False),
                "explanation" : logic_result.get("explanation", "")
            }

    # --- ASSIGNMENT (CSP) ---
    if csp_result:
        if csp_result.get("decision") == "accepted":
            slot = csp_result.get("assigned_slot")
            response["assignment"] = {
                "room"      : csp_result.get("assigned_room", ""),
                "slot"      : slot,
                "slot_time" : SLOT_TIMES.get(slot, ""),
                "notes"     : csp_result.get("notes", "")
            }
        else:
            response["decision"] = "rejected"
            response["message"]  = f"No slot available: {csp_result.get('notes','')}"
            return response

    # --- ROUTE (Search) ---
    if search_result:
        path = search_result.get("path", [])
        response["route"] = {
            "algorithm" : search_result.get("algorithm_used", ""),
            "path"      : path,
            "path_str"  : " -> ".join(path),
            "cost"      : search_result.get("cost", 0),
            "steps"     : search_result.get("steps", 0)
        }

    # --- FINAL DECISION & MESSAGE ---
    response["decision"] = "accepted" if not rejected else "rejected"

    # build message based on request type
    name = request_obj.get("name", "User")
    if request_type == "Navigation_Only":
        path_str = response["route"].get("path_str", "")
        response["decision"] = "completed"
        response["message"]  = (
            f"Route generated for {name}. "
            f"Follow: {path_str}"
        )
    elif request_type == "Eligibility_Check":
        pass  # already handled above
    elif request_type == "Booking_or_Scheduling":
        room = response["assignment"].get("room", "")
        slot = response["assignment"].get("slot", "")
        time = response["assignment"].get("slot_time", "")
        response["message"] = (
            f"Booking confirmed for {name}. "
            f"Room: {room}, Slot {slot} ({time})."
        )
    elif request_type in ["Urgent_Service_Request", "Full_Service_Request"]:
        room     = response["assignment"].get("room", "")
        slot     = response["assignment"].get("slot", "")
        time     = response["assignment"].get("slot_time", "")
        priority = response["priority"].get("final_priority", "")
        path_str = response["route"].get("path_str", "")
        response["message"] = (
            f"Request accepted for {name}. "
            f"Priority: {priority.upper()}. "
            f"Assigned {room}, Slot {slot} ({time}). "
            f"Route: {path_str}."
        )

    return response


# ----------------------------------------------------------
# DISPLAY FUNCTION
# Prints final response in clean CLI format
# ----------------------------------------------------------
def display_final_response(response):
    """
    Prints the final response to CLI in readable format.
    Only shows sections that have data.
    """
    print()
    print("=" * 56)
    print("           SMART CAMPUS AI — FINAL RESPONSE")
    print("=" * 56)
    print(f"  Request ID : {response['request_id']}")
    print(f"  Decision   : {response['decision'].upper()}")

    # priority
    if response.get("priority"):
        p = response["priority"]
        print()
        print("  [PRIORITY]")
        print(f"    Perceptron (Binary) : {p.get('binary_priority','').upper()}")
        print(f"    MLP (Final)         : {p.get('final_priority','').upper()}")
        print(f"    Confidence          : {p.get('confidence', 0.0)}")

    # eligibility
    if response.get("eligibility"):
        e = response["eligibility"]
        print()
        print("  [ELIGIBILITY]")
        if "entailed" in e:
            print(f"    Entailed    : {e['entailed']}")
        if "allowed" in e:
            print(f"    Allowed     : {e['allowed']}")
        print(f"    Explanation : {e.get('explanation','')}")

    # assignment
    if response.get("assignment"):
        a = response["assignment"]
        print()
        print("  [ASSIGNMENT]")
        print(f"    Room      : {a.get('room','')}")
        print(f"    Slot      : {a.get('slot','')}")
        print(f"    Time      : {a.get('slot_time','')}")
        if a.get("notes"):
            print(f"    Note      : {a.get('notes','')}")

    # route
    if response.get("route"):
        r = response["route"]
        print()
        print("  [ROUTE]")
        print(f"    Algorithm : {r.get('algorithm','')}")
        print(f"    Path      : {r.get('path_str','')}")
        print(f"    Cost      : {r.get('cost', 0)}")
        print(f"    Steps     : {r.get('steps', 0)}")

    print()
    print(f"  Message: {response['message']}")
    print("=" * 56)