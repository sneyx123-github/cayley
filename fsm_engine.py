# fsm_engine.py

from typing import Any, Dict, List, Tuple

# SEE ALSO: modFSM_spec.py

# ----------------------------------------
# FSM-Spezifikation (extern definiert)
# ----------------------------------------
# Beispielstruktur:
# modFSM_spec = {
#     "active": {
#         "unload": {
#             "condition": "params['error_level'] < 3",
#             "next": "terminated",
#             "actions": [
#                 {"type": "call", "name": "release_resources"},
#                 {"type": "send", "target": "manager", "event": "reset", "params": {"reason": "unload"}}
#             ]
#         }
#     }
# }

# ----------------------------------------
# FSM-Transition mit Bedingungsauswertung
# ----------------------------------------
def fsm_transition(
    current_state: str,
    event: Dict[str, Any],
    context: Dict[str, Any],
    spec: Dict[str, Dict[str, Dict[str, Any]]]
) -> Tuple[str, List[Dict[str, Any]]]:
    entry = spec.get(current_state, {}).get(event["name"])
    if not entry:
        return current_state, []

    cond = entry.get("condition")
    if cond:
        try:
            if not eval(cond, {}, {"params": event["params"], "context": context}):
                return current_state, []
        except Exception:
            return current_state, []

    next_state = entry["next"]
    actions = entry.get("actions", [])
    return next_state, actions

# ----------------------------------------
# FSM-Anwendung auf Registry-Modul
# ----------------------------------------
def apply_event_to_module(
    module_name: str,
    event: Dict[str, Any],
    registry: Dict[str, Dict[str, Any]],
    spec: Dict[str, Dict[str, Dict[str, Any]]]
) -> Tuple[str, List[Dict[str, Any]]]:
    current_state = registry.get(module_name, {}).get("fsm_state", "unset")
    context = registry.get(module_name, {})
    next_state, actions = fsm_transition(current_state, event, context, spec)

    registry[module_name]["fsm_state"] = next_state
    registry[module_name]["fsm_action_log"] = actions
    return next_state, actions

# ----------------------------------------
# FSM-Diagnose: gültige Events für Zustand
# ----------------------------------------
def valid_events(state: str, spec: Dict[str, Dict[str, Any]]) -> List[str]:
    return list(spec.get(state, {}).keys())

# ----------------------------------------
# FSM-Diagnose: alle erreichbaren Zustände
# ----------------------------------------
def reachable_states(spec: Dict[str, Dict[str, Any]]) -> List[str]:
    states = set()
    for events in spec.values():
        for trans in events.values():
            states.add(trans["next"])
    return sorted(states)

# ----------------------------------------
# FSM-Spezifikation als Pandas-Tabelle
# ----------------------------------------
def spec_to_dataframe(spec: Dict[str, Dict[str, Any]]):
    import pandas as pd
    rows = []
    for state, events in spec.items():
        for event, trans in events.items():
            cond = trans.get("condition", "")
            next_state = trans["next"]
            actions = trans.get("actions", [])
            action_str = "; ".join(
                f"{a['type']}:{a.get('name', a.get('event'))}" for a in actions
            )
            rows.append({
                "From": state,
                "Event": event,
                "Condition": cond,
                "To": next_state,
                "Actions": action_str
            })
    return pd.DataFrame(rows)

