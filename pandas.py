import pandas as pd
import json
import sys
import os
from cayley.module_registry import _registry
from cayley.module_info import scan_sysmodules
from cayley.modFSM_spec import modFSM_spec_prelife
from cayley.fsm_engine import spec_to_dataframe

# === Tabellenfunktionen mit Kürzeln ===

def hh():
    print("Tabellenübersicht:")
    print(" od  →  on disk Registry")
    print(" sm  →  sys.modules mit Cluster-Erkennung")
    print(" rg  →  Registry-Zustände (in-memory)")
    print(" cs  →  Cluster-Zusammenfassung")
    print(" fa  → FSM-Aktionslog")
    print(" st  → FSM-Zustandstabelle")
    print(" fm  → FSM-Specification")

def od():
    meta_path = r"C:\Users\simon\AppData\Roaming\Python\Python311\site-packages\cayley\module_registry.json"
    df_meta = load_meta_table(meta_path).sort_values(by="Status")
    print_aligned_table(df_meta, title="Module Registry")

def sm():
    if 1:
        df = sysmodules_table()
        print_aligned_table(df, title="sys.modules Overview")
    else:
        df = pd.DataFrame(scan_sysmodules())
        print(df[["name", "cluster", "mod_type", "file"]].sort_values(by="cluster").to_markdown(index=False))

def rg():
    if 1:
        df = registry_to_dataframe(_registry)
        print_aligned_table(df, title="IN MEMORY REGISTRY")
    else:
        df = registry_to_dataframe(_registry)
        print(df.to_markdown(index=False))

def cs():
    if 1:
        df_sysmod = sysmodules_table()
        df_clust = cluster_summary(df_sysmod)
        filtered = df_clust.loc[df_clust["Module Count"] > 1]
        #print_aligned_table(df_clust, title="Recognized Package Cluster")
        print_aligned_table(filtered, title="Recognized Package Cluster")
    else:
        df = registry_to_dataframe(_registry)
        summary = df.groupby("Cluster").agg({
            "Name": "count",
            "State": lambda x: ", ".join(sorted(set(x))),
            "Dir": lambda x: x.mode().iloc[0] if not x.mode().empty else "n/a"
        }).rename(columns={"Name": "Module Count"})
        print(summary[summary["Module Count"] > 1].sort_values(by="Module Count", ascending=False).to_markdown())

def fa():
    df = registry_to_dataframe(_registry)
    print(df[["Name", "Actions"]].to_markdown(index=False))

def st():
    df = registry_to_dataframe(_registry)
    print(df[["Name", "State", "Cluster"]].sort_values(by="Cluster").to_markdown(index=False))

def fm():
    print("\n=== Module FSM SPEC ===")
    print(spec_to_dataframe(modFSM_spec_prelife).to_markdown(index=False))

# -------------------------------
# Meta-Tabelle aus Registry-Datei
# -------------------------------
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


# -------------------------------
# sys.modules-Tabelle introspektiv
# -------------------------------
def sysmodules_table():
	rows = []

	for name, mod in sys.modules.items():
		file = getattr(mod, "__file__", None)

		if not file:
			mod_type = "builtin"
			path = "n/a"
			basename = ""
			dirname = ""
		else:
			path = os.path.abspath(file)
			dirname = os.path.dirname(path)
			basename = os.path.basename(path)
			init_path = os.path.join(dirname, "__init__.py")
			is_package = os.path.isfile(init_path)
			mod_type = "package" if is_package else "standalone"
			if ".zip" in path:
				mod_type = "zip"

		# Cluster detection: first 2–3 segments of dotted name
		parts = name.split(".")
		cluster = ".".join(parts[:3]) if len(parts) >= 3 else ".".join(parts[:2]) if len(parts) >= 2 else parts[0]

		rows.append({
			"Name": name,
			"Cluster": cluster,
			"Type": mod_type,
			"File": path,
			"Base": basename,
			"Dir": dirname
		})

	df = pd.DataFrame(rows)
	return df.sort_values(by=["Cluster", "Name"])

# -------------------------------
# Tabellendruck mit Ausrichtung
# -------------------------------
def print_aligned_table(df, title=None):
    if title:
        print(f"\n=== {title} ===")

    align_left = [col for col in df.columns if df[col].dtype == "object"]
    align_right = [col for col in df.columns if df[col].dtype != "object"]

    col_widths = {col: max(df[col].astype(str).map(len).max(), len(col)) for col in df.columns}
    header = " | ".join(
        f"{col:<{col_widths[col]}}" if col in align_left else f"{col:>{col_widths[col]}}"
        for col in df.columns
    )
    separator = "-+-".join("=" * col_widths[col] for col in df.columns)
    print(header)
    print(separator)

    for _, row in df.iterrows():
        line = " | ".join(
            f"{str(row[col]):<{col_widths[col]}}" if col in align_left else f"{str(row[col]):>{col_widths[col]}}"
            for col in df.columns
        )
        print(line)

def cluster_summary(df):
    return df.groupby("Cluster").agg({
        "Name": "count",
        "Type": lambda x: ", ".join(sorted(set(x))),
        "Dir": lambda x: x.mode().iloc[0] if not x.mode().empty else "n/a"
    }).rename(columns={"Name": "Module Count"})



# === Registry → DataFrame ===

def registry_to_dataframe(registry: dict):
    rows = []
    for name, meta in registry.items():
        rows.append({
            "Name": name,
            "State": meta.get("fsm_state", "unset"),
            "Cluster": meta.get("cluster", ""),
            "Type": meta.get("mod_type", ""),
            "Dir": meta.get("dir", ""),
            "Hash": meta.get("file_hash", ""),
            "Depends": ", ".join(meta.get("depends_on", [])) if "depends_on" in meta else "",
            "Actions": "; ".join(str(a) for a in meta.get("fsm_action_log", [])) if "fsm_action_log" in meta else ""
        })
    return pd.DataFrame(rows)

# === Main-Testsequenz ===

def main():
    hh()
    od()
    sm()
    rg()
    cs()
    fa()
    st()
    fm()

if __name__ == "__main__":
    main()

