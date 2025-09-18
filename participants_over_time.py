# plot_participants_matrix.py
# Usage: python plot_participants_matrix.py
# Requires: pandas, plotly

import re
import glob
import os
import pandas as pd
import plotly.express as px

INPUT_GLOB = "data/Participants/*.csv"
OUTPUT_HTML = "participants_matrix.html"

def term_to_sort_date(term):
    # Map SoSeYYYY -> YYYY + 0.25 (spring/summer)
    # Map WiSeYY-YY -> start_year + 0.75 (autumn/winter)
    m = re.match(r"SoSe(\d{2,4})$", term)
    if m:
        y = int(m.group(1))
        if y < 100:
            y = 2000 + y
        return y + 0.25
    m = re.match(r"WiSe(\d{2,4})-(\d{2,4})$", term)
    if m:
        y1 = int(m.group(1))
        if y1 < 100:
            y1 = 2000 + y1
        return y1 + 0.75
    # fallback: try to extract a year
    m = re.search(r"(\d{4})", term)
    if m:
        return int(m.group(1)) + 0.5
    m = re.search(r"(\d{2})", term)
    if m:
        return 2000 + int(m.group(1)) + 0.5
    return 0

def load_counts(input_glob=INPUT_GLOB):
    files = sorted(glob.glob(input_glob))
    if not files:
        raise FileNotFoundError(f"No files matched {input_glob}. Run the script where your data directory is available.")
    rows = []
    for f in files:
        fname = os.path.basename(f)
        parts = fname.split('_')
        if len(parts) < 3:
            # skip unexpected filenames
            continue
        term = parts[0]
        course = parts[1]
        try:
            df = pd.read_csv(f)
        except Exception:
            df = pd.read_csv(f, encoding='latin-1')
        # Count rows where at least one name column is present, fall back to non-empty row count.
        if {'Vorname','Nachname'}.issubset(df.columns):
            count = int(df[['Vorname','Nachname']].notna().any(axis=1).sum())
        else:
            count = int(df.dropna(how='all').shape[0])
        rows.append({"term": term, "course": course, "count": count})
    return pd.DataFrame(rows)

def build_pivot(df_counts):
    # aggregate duplicates (if any), pivot and order by chronological term order
    grouped = df_counts.groupby(['term','course'], as_index=False)['count'].sum()
    pivot = grouped.pivot(index='term', columns='course', values='count')
    ordered_terms = sorted(pivot.index.tolist(), key=term_to_sort_date)
    pivot = pivot.reindex(index=ordered_terms)
    return pivot.fillna(0).astype(int)

def plot_and_save(pivot, out_html=OUTPUT_HTML):
    pivot_display = pivot
    fig = px.imshow(
        pivot_display.values,
        labels=dict(x="Course", y="Term", color="Participants"),
        x=pivot_display.columns.tolist(),
        y=pivot_display.index.tolist(),
        text_auto=True,
        origin='upper',   # ensures first row (earliest term) appears at the top -> time increases downwards
        aspect="auto",
    )
    fig.update_layout(
        title="Participants per Course over Time (rows = terms; time increases downwards)",
        xaxis_title="Course",
        yaxis_title="Term",
        width=1100,
        height=30 + 40 * max(6, len(pivot_display.index))
    )
    fig.write_html(out_html, include_plotlyjs='cdn')
    print(f"Saved interactive plot to {out_html}")

def main():
    df_counts = load_counts()
    pivot = build_pivot(df_counts)
    print("Pivot table (terms x courses) — top rows:")
    print(pivot.head(20).to_string())
    plot_and_save(pivot)

if __name__ == "__main__":
    main()
