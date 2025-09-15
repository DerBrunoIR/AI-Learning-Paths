import pandas as pd
import glob
import plotly.express as px

# Load all CSVs
files = glob.glob("data/Participants/*.csv")
all_data = []

for f in files:
    df = pd.read_csv(f)
    df['Participant'] = df['Vorname'].str.strip() + ' ' + df['Nachname'].str.strip()
    df['Course'] = f.split('_')[-2]
    all_data.append(df[['Participant', 'Course']])

df_all = pd.concat(all_data, ignore_index=True)

# Create sets for each course
courses = ['MI1','MI2','ML1','AML','ML2','AMLS','DL1','DL2']
course_sets = {course: set(df_all[df_all['Course'] == course]['Participant']) for course in courses}

# Conditional probability matrix
cond_matrix = pd.DataFrame(index=courses, columns=courses, dtype=float)

for c1 in courses:
    for c2 in courses:
        if len(course_sets[c1]) > 0:
            cond_matrix.loc[c1, c2] = len(course_sets[c1].intersection(course_sets[c2])) / len(course_sets[c1])
        else:
            cond_matrix.loc[c1, c2] = 0.0

# Visualize the conditional probability matrix
fig = px.imshow(
    cond_matrix.values,
    x=cond_matrix.columns,
    y=cond_matrix.index,
    color_continuous_scale='Blues',
    text_auto='.2f',
    labels=dict(x="Course B", y="Course A", color="P(B|A)"),
    title="Conditional Probability Matrix of Participants Across Courses"
)
fig.show()

