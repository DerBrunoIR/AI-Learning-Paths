import pandas as pd
from pathlib import Path
import plotly.express as px

# Path to participant files
data_path = Path("data/Participants")
files = list(data_path.glob("*_Participants.csv"))

# Dictionary to store participants for each course
course_participants = {}

for file in files:
    # Extract course from filename
    # Example: SoSe2020_MI2_Participants.csv -> MI2
    course = file.stem.split("_")[1]
    
    # Read CSV
    df = pd.read_csv(file)
    
    # Create full name column
    df['FullName'] = df['Vorname'].str.strip() + " " + df['Nachname'].str.strip()
    
    # Initialize set if course not seen before
    if course not in course_participants:
        course_participants[course] = set()
    
    # Add participants to course set
    course_participants[course].update(df['FullName'].dropna())

# Compute union of all participants
all_participants = set().union(*course_participants.values())
course_participants['ALL'] = all_participants

# Prepare data for visualization
course_sizes = {course: len(names) for course, names in course_participants.items()}
course_sizes = dict(sorted(course_sizes.items(), key=lambda x: x[1], reverse=True))  # largest to smallest

# Create a bar chart
fig = px.bar(
    x=list(course_sizes.values()),
    y=list(course_sizes.keys()),
    orientation='h',
    labels={'x': 'Number of Participants', 'y': 'Course'},
    title='Number of Participants per Course (All Terms)'
)

# Reverse y-axis to have largest on the right
fig.update_layout(yaxis=dict(autorange="reversed"))
fig.show()
