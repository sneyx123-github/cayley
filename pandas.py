import pandas as pd
import json
import sys
import os

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
if 0:
    def sysmodules_table():
        rows = []

        for name, mod in sys.modules.items():
            file = getattr(mod, "__file__", None)
            if not file:
                mod_type = "builtin"
                path = "n/a"
            else:
                path = os.path.abspath(file)
                dirname = os.path.dirname(path)
                basename = os.path.basename(path)
                init_path = os.path.join(dirname, "__init__.py")
                is_package = os.path.isfile(init_path)
                mod_type = "package" if is_package else "standalone"
                if ".zip" in path:
                    mod_type = "zip"

            rows.append({
                "Name": name,
                "Type": mod_type,
                "File": path,
                "Base": basename,
                "Dir": dirname
            })

        df = pd.DataFrame(rows)
        return df.sort_values(by="Type")
else:
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

			rows.append({
				"Name": name,
				"Type": mod_type,
				"File": path,
				"Base": basename,
				"Dir": dirname
			})

		df = pd.DataFrame(rows)
		return df.sort_values(by="Type")

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

# -------------------------------
# Main: beide(+1) Tabellen ausgeben
# -------------------------------
if 0:
	if __name__ == "__main__":
		meta_path = r"C:\Users\simon\AppData\Roaming\Python\Python311\site-packages\cayley\module_registry.json"
		df_meta = load_meta_table(meta_path).sort_values(by="Status")
		df_sysmod = sysmodules_table()

		print_aligned_table(df_meta, title="Module Registry")
		print_aligned_table(df_sysmod, title="sys.modules Overview")

else:
	if __name__ == "__main__":
		meta_path = r"C:\Users\simon\AppData\Roaming\Python\Python311\site-packages\cayley\module_registry.json"
		df_meta = load_meta_table(meta_path).sort_values(by="Status")
		df_sysmod = sysmodules_table()

		print_aligned_table(df_meta, title="Module Registry")
		print_aligned_table(df_sysmod, title="sys.modules Overview")

		# Dritte Tabelle: sortierte, einzigartige Verzeichnisse
		unique_dirs = (
			df_sysmod["Dir"]
			.dropna()
			.unique()
			.tolist()
		)
		unique_dirs = sorted(set(unique_dirs))

		df_dirs = pd.DataFrame({"Dir": unique_dirs})
		print_aligned_table(df_dirs, title="Unique Module Directories")

