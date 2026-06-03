import pandas as pd

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

        hub_type = "Connector Hub" if pc_val == "2" else "Module Hub"

        hubs_list.append({
            "Gene"    : gene,
            "Module"  : module,
            "PC"      : pc_val,
            "Hub Type": hub_type
        })
    i += 1

# -------------------- Remove duplicates --------------------
df = pd.DataFrame(hubs_list)
df = df.drop_duplicates(subset=["Gene"])

# -------------------- Print --------------------
print("=" * 50)
print(f"{'Gene':<20} {'Module':<10} {'Hub Type'}")
print("=" * 50)
for _, row in df.iterrows():
    print(f"{row['Gene']:<20} {row['Module']:<10} {row['Hub Type']}")

print(f"\nTotal unique hubs  : {len(df)}")
print(f"Connector hubs (2) : {len(df[df['PC']=='2'])}")
print(f"Module hubs    (1) : {len(df[df['PC']=='1'])}")

print(f"\n🔹 Connector Hubs:")
for g in df[df['PC']=='2']['Gene'].tolist():
    print(f"  {g}")

print(f"\n🔹 Module Hubs:")
for g in df[df['PC']=='1']['Gene'].tolist():
    print(f"  {g}")

# -------------------- Save --------------------
df.to_excel("hub_genes_list.xlsx", index=False)
print(f"\n✅ Saved hub_genes_list.xlsx")