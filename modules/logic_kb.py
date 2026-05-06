# ============================================================
# logic_kb.py
# Purpose : Logic / Knowledge Base Module.
#           Rule-based reasoning engine.
#           Checks eligibility, role authorization, and
#           whether facts can be entailed from the KB.
#           Acts as gatekeeper — if rejected here, system
#           stops and does not proceed to CSP.
# Used by : main.py
# ============================================================

from data.knowledge_base import (
    FACTS,
    RULES,
    ROLE_PERMISSIONS,
    CATEGORY_ROLE_MAP
)


# ----------------------------------------------------------
# HELPER: apply_rules
# Forward chaining — derives new facts from existing ones
# Keeps running until no new facts can be derived
# ----------------------------------------------------------
def apply_rules(facts):
    """
    Forward chaining inference engine.
    Takes current facts set, applies all rules repeatedly.
    Adds newly derived facts until nothing new can be added.
    Returns expanded facts set with all derived facts.
    """
    # work on a copy so original KB is not modified
    derived = set(facts)
    changed = True

    while changed:
        changed = False
        for conditions, conclusion in RULES:
            # try to find a variable binding that satisfies all conditions
            # we look for {x} substitutions
            bindings = find_bindings(conditions, derived)
            for binding in bindings:
                # apply binding to conclusion
                new_fact = conclusion
                for var, val in binding.items():
                    new_fact = new_fact.replace("{" + var + "}", val)
                if new_fact not in derived:
                    derived.add(new_fact)
                    changed = True

    return derived


# ----------------------------------------------------------
# HELPER: find_bindings
# Finds all variable substitutions that satisfy conditions
# ----------------------------------------------------------
def find_bindings(conditions, facts):
    """
    Tries to find all variable bindings {x} = value
    that make all conditions true in current facts.
    Returns list of binding dicts e.g. [{'x': 'Ali'}, ...]
    """
    # start with empty binding
    all_bindings = [{}]

    for condition in conditions:
        new_bindings = []
        for binding in all_bindings:
            # apply existing binding to condition
            cond_applied = condition
            for var, val in binding.items():
                cond_applied = cond_applied.replace("{" + var + "}", val)

            if "{x}" in cond_applied:
                # try all possible values for {x}
                for fact in facts:
                    new_binding = try_match(cond_applied, fact, dict(binding))
                    if new_binding is not None:
                        new_bindings.append(new_binding)
            else:
                # no variable — just check if fact exists
                if cond_applied in facts:
                    new_bindings.append(binding)

        all_bindings = new_bindings

    return all_bindings


# ----------------------------------------------------------
# HELPER: try_match
# Tries to match a condition pattern against a fact
# ----------------------------------------------------------
def try_match(pattern, fact, binding):
    """
    Tries to match pattern (with {x}) against a fact string.
    If {x} appears in pattern, extracts the value from fact.
    Returns updated binding if match succeeds, else None.
    """
    if "{x}" not in pattern:
        return binding if pattern == fact else None

    # split pattern around {x} to find prefix and suffix
    parts = pattern.split("{x}")
    prefix = parts[0]
    suffix = parts[1] if len(parts) > 1 else ""

    if not fact.startswith(prefix):
        return None
    remaining = fact[len(prefix):]

    if suffix:
        if not remaining.endswith(suffix):
            return None
        value = remaining[: len(remaining) - len(suffix)]
    else:
        value = remaining

    if not value:
        return None

    # check if {x} already bound to a different value
    if "x" in binding and binding["x"] != value:
        return None

    new_binding = dict(binding)
    new_binding["x"] = value
    return new_binding


# ----------------------------------------------------------
# FUNCTION: check_eligibility_query
# Handles Eligibility_Check request type
# Checks if a query fact can be entailed from KB
# ----------------------------------------------------------
def check_eligibility_query(query):
    """
    Takes a query string like 'UsesLab(DrKhan, Lab1)'.
    Runs forward chaining on KB.
    Returns whether the query is entailed and explanation.
    """
    # run forward chaining to derive all possible facts
    all_facts = apply_rules(FACTS)

    if query in all_facts:
        # find chain of reasoning
        explanation = build_explanation(query, all_facts)
        return {
            "entailed"    : True,
            "query"       : query,
            "explanation" : explanation
        }
    else:
        return {
            "entailed"    : False,
            "query"       : query,
            "explanation" : f"'{query}' could not be derived from the knowledge base."
        }


# ----------------------------------------------------------
# HELPER: build_explanation
# Builds a human readable reasoning chain
# ----------------------------------------------------------
def build_explanation(query, all_facts):
    """
    Builds a simple explanation of how the query was derived.
    Shows relevant facts and rules that led to conclusion.
    """
    lines = []
    lines.append(f"Query '{query}' is entailed. Reasoning:")

    # extract entity name from query (simple extraction)
    # e.g. UsesLab(DrKhan, Lab1) → entity = DrKhan
    entity = None
    if "(" in query:
        inner = query[query.index("(") + 1: query.index(")")]
        parts = [p.strip() for p in inner.split(",")]
        if parts:
            entity = parts[0]

    if entity:
        relevant = [f for f in all_facts if entity in f]
        for fact in sorted(relevant):
            lines.append(f"  • {fact}")

    return "\n".join(lines)


# ----------------------------------------------------------
# FUNCTION: check_service_eligibility
# Handles Booking, Urgent, Full_Service requests
# Checks if user is allowed to request this service
# ----------------------------------------------------------
def check_service_eligibility(name, role, category):
    """
    Checks if a user is allowed to request a specific service.
    Steps:
      1. Check if role is allowed for this category
      2. Run forward chaining to check user-specific rules
      3. Return allowed True/False with explanation
    """
    explanation_lines = []

    # step 1 — check role permission for category
    allowed_roles = CATEGORY_ROLE_MAP.get(category, [])
    if role not in allowed_roles:
        return {
            "allowed"     : False,
            "explanation" : (
                f"Role '{role}' is not permitted to request '{category}'. "
                f"Allowed roles: {', '.join(allowed_roles)}."
            )
        }
    explanation_lines.append(
        f"Role '{role}' is permitted for '{category}'."
    )

    # step 2 — run forward chaining
    all_facts = apply_rules(FACTS)

    # check if user can request this category
    can_request_fact = f"CanRequest({name}, {category})"

    if can_request_fact in all_facts:
        explanation_lines.append(
            f"'{name}' satisfies eligibility rules for '{category}'."
        )
        return {
            "allowed"     : True,
            "explanation" : " | ".join(explanation_lines)
        }

    # check if user exists in KB at all
    user_known = any(name in f for f in all_facts)
    if not user_known:
        return {
            "allowed"     : False,
            "explanation" : (
                f"User '{name}' not found in knowledge base. "
                "Please register with the campus system first."
            )
        }

    # user exists but not eligible
    return {
        "allowed"     : False,
        "explanation" : (
            f"'{name}' does not satisfy eligibility conditions "
            f"for '{category}'. Prerequisites may not be completed."
        )
    }


# ----------------------------------------------------------
# MAIN FUNCTION: run_logic
# Called by pipeline — routes to correct logic function
# ----------------------------------------------------------
def run_logic(request_obj):
    """
    Main Logic/KB function called by the pipeline.
    Routes to correct checker based on request_type.
    Returns (success, logic_result_dict)
    """
    request_type = request_obj.get("request_type", "")
    name         = request_obj.get("name", "")
    role         = request_obj.get("role", "")
    category     = request_obj.get("category", "")
    query        = request_obj.get("query", "")

    # --- Eligibility_Check: check if query is entailed ---
    if request_type == "Eligibility_Check":
        if not query:
            return False, {
                "allowed"     : False,
                "explanation" : "No query provided for eligibility check."
            }
        result = check_eligibility_query(query)
        return True, result

    # --- Other types: check service eligibility ---
    else:
        result = check_service_eligibility(name, role, category)
        return True, result