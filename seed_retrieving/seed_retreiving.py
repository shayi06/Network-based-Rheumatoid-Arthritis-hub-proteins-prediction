import pandas as pd
import stringdb
from mygene import MyGeneInfo
import requests

# ===== FILE PATHS =====
INPUT_FILE  = r"D:\abi\abi\pythonProject\Abi 2025\Research\network\seed_retrieving\ra_133_proteins.xlsx"
OUTPUT_FILE = r"D:\abi\abi\pythonProject\Abi 2025\Research\network\seed_retrieving\processed_protein.xlsx"
API_BASE    = "https://rest.uniprot.org"

# ===== 1. LOAD & CLEAN DATA =====
data = pd.read_excel(INPUT_FILE).drop_duplicates()

if "Gene_x" in data.columns:
    data.rename(columns={"Gene_x": "Gene"}, inplace=True)

if "Gene" not in data.columns:
    raise ValueError("Input file must contain a 'Gene' or 'Gene_x' column.")

print(f"Total genes loaded: {len(data)}")

# ===== 2. GENE → PROTEIN NAME =====
mg      = MyGeneInfo()
genes   = data['Gene'].dropna().unique().tolist()
results = mg.querymany(genes, scopes='symbol', fields='name,entrezgene', species='human')

protein_map = {
    res["query"]: res["name"]
    for res in results
    if not res.get("notfound") and "name" in res
}

data["Protein Name"] = data["Gene"].map(protein_map)
data = data.dropna(subset=["Protein Name"])
print(f"Genes mapped to protein names: {len(data)}")

# ===== 3. GET STRING IDs =====
string_ids = stringdb.get_string_ids(data["Protein Name"].tolist(), species=9606)
string_ids = string_ids.drop_duplicates(subset="stringId", keep="first").reset_index(drop=True)
print(f"STRING IDs retrieved: {len(string_ids)}")

# ===== 4. FETCH UNIPROT ANNOTATIONS (all proteins, no skipping) =====
string_ids["Uniprot accession"]    = ""
string_ids["Evidences"]            = ""
string_ids["Biological Processes"] = ""

for i, row in string_ids.iterrows():
    entry = row['stringId']
    try:
        r = requests.get(
            f"{API_BASE}/uniprotkb/search",
            params={"query": f"{entry} AND (taxonomy_id:9606)", "size": 1},
            timeout=10
        )
        r.raise_for_status()
        records = r.json().get("results", [])

        if not records:
            continue

        rec = records[0]
        acc = rec.get("primaryAccession", "")

        evi_manual, proc_manual = [], []
        evi_comp,   proc_comp   = [], []

        for xref in rec.get("uniProtKBCrossReferences", []):
            if xref.get("database") != "GO":
                continue
            for prop in xref.get("properties", []):
                if not prop.get("value", "").startswith("P:"):
                    continue
                go_term  = prop["value"][2:]
                evidence = next(
                    (p["value"] for p in xref["properties"]
                     if "evidence" in p.get("key", "").lower()),
                    ""
                )
                if "IEA" not in evidence:
                    evi_manual.append(evidence)
                    proc_manual.append(go_term)
                else:
                    evi_comp.append(evidence)
                    proc_comp.append(go_term)

        # Store accession always
        string_ids.at[i, "Uniprot accession"] = acc

        # Prefer manual, fallback to computational
        if evi_manual:
            string_ids.at[i, "Evidences"]            = ", ".join(evi_manual)
            string_ids.at[i, "Biological Processes"] = ", ".join(proc_manual)
        elif evi_comp:
            string_ids.at[i, "Evidences"]            = ", ".join(evi_comp)
            string_ids.at[i, "Biological Processes"] = ", ".join(proc_comp)

    except Exception as e:
        print(f"⚠️ Failed for {entry}: {e}")

# ===== 5. SPLIT CATEGORIES (for info only) =====
manual        = string_ids[
    string_ids["Evidences"].notna() &
    (~string_ids["Evidences"].str.contains("IEA", na=False)) &
    (string_ids["Evidences"] != "")
].reset_index(drop=True)

computational = string_ids[
    string_ids["Evidences"].str.contains("IEA", na=False)
].reset_index(drop=True)

no_annotation = string_ids[
    string_ids["Evidences"] == ""
].reset_index(drop=True)

print(f"\nManual evidence proteins:        {len(manual)}")
print(f"Computational evidence proteins: {len(computational)}")
print(f"No annotation proteins:          {len(no_annotation)}")

# ===== 6. SAVE MANUAL SHEET ONLY =====
string_ids.to_excel(OUTPUT_FILE, index=False)
print(f"\n✅ Saved all {len(string_ids)} proteins to: {OUTPUT_FILE}")