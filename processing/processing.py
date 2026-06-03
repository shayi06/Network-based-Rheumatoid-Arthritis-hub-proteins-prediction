import pandas as pd

# -------------------- Load seeds --------------------
data  = pd.read_excel(r"D:\abi\abi\pythonProject\Abi 2025\Research\network\seed_retrieving\processed_protein.xlsx")
seeds = set(data["preferredName"].dropna().tolist())
print(f"✅ Seeds loaded: {len(seeds)}")

# -------------------- Parse hubs --------------------
hubs_list = []

with open(r"D:\abi\abi\pythonProject\Abi 2025\Research\network\sub_network\human_RA_hubs.txt", "r") as file:
    lines = file.readlines()

i = 0
while i < len(lines):
    line = lines[i].strip()

    if line.startswith("Node:"):
        gene   = line.replace("Node:", "").strip()
        module = ""
        pc_val = ""

        for j in range(i+1, min(i+6, len(lines))):
            l = lines[j].strip()
            if l.startswith("module:"):
                module = l.replace("module:", "").strip()
            if l in ["1", "2"]:
                pc_val = l

        hub_type  = "Connector Hub" if pc_val == "2" else "Module Hub"
        seed_status = "Seed" if gene in seeds else "Non-seed"

        hubs_list.append({
            "Gene"       : gene,
            "Module"     : module,
            "PC"         : pc_val,
            "Hub Type"   : hub_type,
            "Seed Status": seed_status
        })
    i += 1

# -------------------- Remove duplicates --------------------
df = pd.DataFrame(hubs_list)
df = df.drop_duplicates(subset=["Gene"])

# -------------------- Print full table --------------------
print("\n" + "=" * 65)
print(f"{'Gene':<20} {'Module':<10} {'Hub Type':<18} {'Seed Status'}")
print("=" * 65)
for _, row in df.iterrows():
    print(f"{row['Gene']:<20} {row['Module']:<10} {row['Hub Type']:<18} {row['Seed Status']}")

# -------------------- Summary --------------------
print(f"\n{'='*65}")
print(f"SUMMARY")
print(f"{'='*65}")
print(f"Total unique hubs      : {len(df)}")
print(f"Connector hubs (pc=2)  : {len(df[df['PC']=='2'])}")
print(f"Module hubs    (pc=1)  : {len(df[df['PC']=='1'])}")
print(f"\nSeed hubs              : {len(df[df['Seed Status']=='Seed'])}")
print(f"Non-seed hubs          : {len(df[df['Seed Status']=='Non-seed'])}")

# -------------------- Connector hubs --------------------
print(f"\n🔹 Connector Hubs (pc=2):")
conn = df[df['PC']=='2']
print(f"  {'Gene':<20} {'Seed Status'}")
print(f"  {'─'*35}")
for _, row in conn.iterrows():
    print(f"  {row['Gene']:<20} {row['Seed Status']}")

print(f"\n  Seed connector hubs     : {len(conn[conn['Seed Status']=='Seed'])}")
print(f"  Non-seed connector hubs : {len(conn[conn['Seed Status']=='Non-seed'])}")

# -------------------- Module hubs --------------------
print(f"\n🔹 Module Hubs (pc=1):")
mod = df[df['PC']=='1']
print(f"  {'Gene':<20} {'Seed Status'}")
print(f"  {'─'*35}")
for _, row in mod.iterrows():
    print(f"  {row['Gene']:<20} {row['Seed Status']}")

print(f"\n  Seed module hubs        : {len(mod[mod['Seed Status']=='Seed'])}")
print(f"  Non-seed module hubs    : {len(mod[mod['Seed Status']=='Non-seed'])}")

# -------------------- Save --------------------
df.to_excel("hub_genes_list.xlsx", index=False)
print(f"\n✅ Saved hub_genes_list.xlsx")

# -------------------- Non-seed hub breakdown --------------------
non_seed = df[df['Seed Status'] == 'Non-seed']

print(f"\n🔹 Non-Seed Hubs Breakdown:")
print(f"  Total non-seed hubs          : {len(non_seed)}")
print(f"  Non-seed Connector hubs (pc=2): {len(non_seed[non_seed['PC']=='2'])}")
print(f"  Non-seed Module hubs    (pc=1): {len(non_seed[non_seed['PC']=='1'])}")

print(f"\n  Non-seed Connector Hubs:")
print(f"  {'Gene':<20} {'Module'}")
print(f"  {'─'*35}")
for _, row in non_seed[non_seed['PC']=='2'].iterrows():
    print(f"  {row['Gene']:<20} {row['Module']}")

print(f"\n  Non-seed Module Hubs:")
print(f"  {'Gene':<20} {'Module'}")
print(f"  {'─'*35}")
for _, row in non_seed[non_seed['PC']=='1'].iterrows():
    print(f"  {row['Gene']:<20} {row['Module']}")

# -------------------- Seed hub breakdown --------------------
seed_df = df[df['Seed Status'] == 'Seed']

print(f"\n🔹 Seed Hubs Breakdown:")
print(f"  Total seed hubs              : {len(seed_df)}")
print(f"  Seed Connector hubs (pc=2)   : {len(seed_df[seed_df['PC']=='2'])}")
print(f"  Seed Module hubs    (pc=1)   : {len(seed_df[seed_df['PC']=='1'])}")