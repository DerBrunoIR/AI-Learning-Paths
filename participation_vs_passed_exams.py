# AI GENERATED

import pandas as pd
from pathlib import Path
import plotly.express as px

def normalize_term(term):
    """Convert terms to a unified format like 'WiSe22' or 'SoSe25'"""
    t = term.strip()
    if t.startswith("WiSe"):
        # Participants: WiSe22-23 -> WiSe22
        return "WiSe" + t.split("WiSe")[1][:2]
    elif t.startswith("SoSe"):
        # Participants: SoSe2025 -> SoSe25
        return "SoSe" + t[-2:]
    elif t[2:6] == "WiSe":  # exam: 22WiSe
        return "WiSe" + t[:2]
    elif t[2:6] == "SoSe":  # exam: 25SoSe
        return "SoSe" + t[:2]
    return t

# === Step 1: Participants per term for ML1 ===
data_path = Path("data/Participants")
files = list(data_path.glob("*_Participants.csv"))

ml1_participants = {}

for file in files:
    if "_ML1_" in file.name:
        raw_term = file.stem.split("_")[0]  # e.g. WiSe20-21
        term = normalize_term(raw_term)
        df = pd.read_csv(file)
        df['FullName'] = df['Vorname'].str.strip() + " " + df['Nachname'].str.strip()
        ml1_participants[term] = len(set(df['FullName'].dropna()))

participants_df = pd.DataFrame(list(ml1_participants.items()), columns=['term','participants'])

# === Step 2: Passed exams per term for ML1 ===
exam_df = pd.read_csv("data/passed_exam_by_coures.csv")
exam_df.columns = exam_df.columns.str.strip()
exam_df['course'] = exam_df['course'].astype(str).str.strip()

# normalize exam terms
exam_df['term'] = exam_df['term'].apply(normalize_term)

exam_df = exam_df[exam_df['course'] == 'ML1']
exam_df['passed'] = exam_df['num_passed'].astype(str).str.strip().astype(int)
exam_df = exam_df[['term','passed']]

# === Step 3: Merge participants and passed ===
merged = participants_df.merge(exam_df, on='term', how='left')
merged['passed'] = merged['passed'].fillna(0).astype(int)

# Melt for grouped bar chart
plot_df = merged.melt(
    id_vars='term',
    value_vars=['participants','passed'],
    var_name='Category',
    value_name='Count'
)

# === Step 4: Plot ===
fig = px.bar(
    plot_df,
    x='term',
    y='Count',
    color='Category',
    barmode='group',
    title='ML1: Participants vs Passed Exams per Term (Normalized Terms)'
)

fig.update_layout(xaxis={'categoryorder':'category ascending'})
fig.show()

print(merged)
