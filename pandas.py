import pandas as pd
import json

def load_meta_table(json_path):
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

def print_aligned_table(df):
    # Spaltenausrichtung definieren
    align_left = ["Module", "Status", "Provides", "Resources", "FSM-State", "Path"]
    align_right = ["Requires"]

    # Spaltenbreiten berechnen
    col_widths = {col: max(df[col].astype(str).map(len).max(), len(col)) for col in df.columns}

    # Header-Zeile
    header = " | ".join(
        f"{col:<{col_widths[col]}}" if col in align_left else f"{col:>{col_widths[col]}}"
        for col in df.columns
    )
    separator = "-+-".join("=" * col_widths[col] for col in df.columns)

    print(header)
    print(separator)

    # Datenzeilen
    for _, row in df.iterrows():
        line = " | ".join(
            f"{str(row[col]):<{col_widths[col]}}" if col in align_left else f"{str(row[col]):>{col_widths[col]}}"
            for col in df.columns
        )
        print(line)

if __name__ == "__main__":
    df = load_meta_table(r"C:\Users\simon\AppData\Roaming\Python\Python311\site-packages\cayley\module_registry.json")
    df_sorted = df.sort_values(by="Status")
    print_aligned_table(df_sorted)

