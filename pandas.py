import pandas as pd
import json

def load_meta_table(json_path="__meta__.json"):
    with open(json_path, "r") as f:
        meta = json.load(f)

    rows = []
    for key, entry in meta.items():
        rows.append({
            "Module": key,
            "Status": entry.get("status", "unknown"),
            "Requires": len(entry.get("requires", [])),
            "Provides": ", ".join(entry.get("provides", [])),
            "Resources": ", ".join(entry.get("resources", [])),
            "FSM-State": entry.get("fsm_state", "unset"),
            "Path": entry.get("sys_path", "unknown")
        })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    json_path = r"C:\Users\simon\AppData\Roaming\Python\Python311\site-packages\cayley\module_registry.json"
    df = load_meta_table(json_path)
    print(df.sort_values(by="Status"))

