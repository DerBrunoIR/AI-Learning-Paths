# AI GENERATED
import pandas as pd
import glob
import plotly.express as px

# 1. Load all CSVs
files = glob.glob("data/Participants/*.csv")
all_data = []

for f in files:
    df = pd.read_csv(f)
    df['Participant'] = df['Vorname'].str.strip() + ' ' + df['Nachname'].str.strip()
    df['Course'] = f.split('_')[-2]  # Extract course from filename
    all_data.append(df[['Participant', 'Course']])

df_all = pd.concat(all_data, ignore_index=True)

# 2. Create sets for each course
courses = ['MI1','MI2','ML1','AML','ML2','AMLS','DL1','DL2']
course_sets = {course: set(df_all[df_all['Course'] == course]['Participant']) for course in courses}

# Union of all participants
all_participants = set(df_all['Participant'])

# 3. Create intersections matrix (size of intersections for all pairs)
matrix = pd.DataFrame(index=courses, columns=courses, dtype=int)

for c1 in courses:
    for c2 in courses:
        matrix.loc[c1, c2] = len(course_sets[c1].intersection(course_sets[c2]))

# 4. Visualize the intersections matrix
fig = px.imshow(
    matrix.values,
    x=matrix.columns,
    y=matrix.index,
    color_continuous_scale='Blues',
    text_auto=True,
    labels=dict(x="Course", y="Course", color="Intersection Size"),
    title="Intersection Matrix of Participants Across Courses"
)
fig.show()

# Optional: show set sizes
set_sizes = {course: len(course_sets[course]) for course in courses}
print("Set sizes per course:", set_sizes)
print("Total unique participants:", len(all_participants))

