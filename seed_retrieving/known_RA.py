import torch
import pandas as pd

# ===== PATHS =====
label_file   = r"D:\abi\abi\pythonProject\Abi 2025\Research\GNN_RA\final_prediction\MIL\labeled_sets\protein_disease_labels.pt"
disease_file = r"D:\abi\abi\pythonProject\Abi 2025\Research\network\seed_retrieving\processed_disease_cleaned.xlsx"
save_file    = r"D:\abi\abi\pythonProject\Abi 2025\Research\network\seed_retrieving\ra_133_proteins.xlsx"

# ===== LOAD ML RA PROTEINS (133) =====
print("🔹 Loading ML label data...")
label_data     = torch.load(label_file, weights_only=False)
protein_labels = label_data['protein_labels']

ml_ra = set(pid for pid, labels in protein_labels.items()
            if 'RHEUMATOID' in labels)
print(f"  ML RA proteins: {len(ml_ra)}")

# ===== LOAD EXCEL =====
print("🔹 Loading disease excel...")
df = pd.read_excel(disease_file)

# ===== FILTER TO 133 INTERSECTION =====
ra_df = df[
    (df['Disease'].str.contains("Rheumatoid", case=False, na=False)) &
    (df['Uniprot accession'].isin(ml_ra))
].drop_duplicates(subset='Uniprot accession')

print(f"  Filtered RA proteins: {len(ra_df)}")

# ===== SAVE =====
ra_df.to_excel(save_file, index=False)
print(f"✅ Saved: {save_file}")