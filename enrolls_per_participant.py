# save as visualize_participants.py and run in the project root (where data/Participants lives)
import os, glob
import pandas as pd
import plotly.express as px

DATA_DIR = 'data/Participants'   # change if your files are elsewhere

# find csv files
files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
print(f'Found {len(files)} CSV files in {DATA_DIR!r}.')

if len(files) == 0:
    raise SystemExit("No CSV files found in data directory. Check path and try again.")

records = []
for f in files:
    basename = os.path.basename(f)
    parts = basename.split('_')
    if len(parts) < 3:
        print(f"Skipping unexpected filename format: {basename}")
        continue
    term, course = parts[0], parts[1]
    # try utf-8, fallback latin-1
    try:
        df = pd.read_csv(f, dtype=str, engine='python', encoding='utf-8')
    except Exception:
        df = pd.read_csv(f, dtype=str, engine='python', encoding='latin-1')
    # normalize expected name columns (Vorname, Nachname)
    cols_lower = {c.lower(): c for c in df.columns}
    if 'vorname' in cols_lower and 'nachname' in cols_lower:
        df = df.rename(columns={cols_lower['vorname']:'Vorname', cols_lower['nachname']:'Nachname'})
    else:
        # fallback: assume first two columns are first/last names
        df.columns = list(df.columns)  # no-op to be safe
        df['Vorname'] = df.iloc[:, 0].astype(str)
        if df.shape[1] > 1:
            df['Nachname'] = df.iloc[:, 1].astype(str)
        else:
            df['Nachname'] = ''
    df['Vorname'] = df['Vorname'].fillna('').astype(str)
    df['Nachname'] = df['Nachname'].fillna('').astype(str)
    df['student'] = (df['Vorname'].str.strip() + ' ' + df['Nachname'].str.strip()).str.replace(r'\s+', ' ', regex=True).str.strip()
    df['course'] = course
    df['term'] = term
    df = df.loc[df['student'] != '', ['student','course','term']].drop_duplicates(subset=['student','course','term'])
    records.append(df)

all_df = pd.concat(records, ignore_index=True)
print(f'Combined rows (unique student-course-term triples): {len(all_df)}')

# number of distinct terms per (course, student)
group = all_df.groupby(['course','student'], as_index=False)['term'].nunique().rename(columns={'term':'terms_count'})
group['terms_count'] = group['terms_count'].astype(int)

# pivot table: for each course, how many students attended in k terms
pivot = group.groupby(['course','terms_count']).size().reset_index(name='num_students')
pivot_table = pivot.pivot(index='course', columns='terms_count', values='num_students').fillna(0).astype(int).sort_index()
print('\nPivot table (rows = course; columns = number of terms; values = number of students):\n')
print(pivot_table)

# prepare stacked-bar data
melted = pivot_table.reset_index().melt(id_vars='course', var_name='terms_count', value_name='num_students')
melted['terms_count'] = melted['terms_count'].astype(int)
melted['terms_count_str'] = melted['terms_count'].astype(str)
course_order = melted.groupby('course')['num_students'].sum().sort_values(ascending=False).index.tolist()

fig_bar = px.bar(
    melted,
    x='course',
    y='num_students',
    color='terms_count_str',
    category_orders={'course': course_order},
    labels={'terms_count_str': 'Terms participated', 'num_students': 'Number of students', 'course': 'Course'},
    title='For each course: how many students participated in 1 / 2 / ... terms (stacked)'
)
fig_bar.update_layout(barmode='stack', xaxis_tickangle=-45)
fig_bar.show()
# save to HTML
fig_bar.write_html('participants_by_terms_stacked_bar.html')
print("Saved stacked-bar to participants_by_terms_stacked_bar.html")

# violin (distribution)
fig_violin = px.violin(
    group.sort_values('course'),
    x='course',
    y='terms_count',
    box=True,
    points='all',
    labels={'terms_count':'Number of terms', 'course':'Course'},
    title='Distribution of number of terms a student participates in each course (per student)'
)
fig_violin.update_layout(xaxis_tickangle=-45)
fig_violin.show()
fig_violin.write_html('participants_terms_distribution_violin.html')
print("Saved violin plot to participants_terms_distribution_violin.html")

# top 5 repeaters per course
top_repeaters = group.sort_values(['course','terms_count'], ascending=[True,False]).groupby('course').head(5)
print('\nTop 5 repeat participants per course (student, terms_count):')
print(top_repeaters.to_string(index=False))

# short summary
summary = group.groupby('course').agg(n_students=('student','nunique'), max_terms=('terms_count','max')).sort_values('n_students', ascending=False)
print('\nSummary by course (unique students & max terms any student attended):\n')
print(summary)
