# AI GENERATED

import pandas as pd
import glob
import itertools
from collections import defaultdict
import plotly.express as px

# Path to participant files
files = glob.glob("data/Participants/*.csv")

# Map course codes
courses = ["MI1", "MI2", "ML1", "ML2", "DL1", "DL2", "AML", "AMLS"]

# Dictionary to hold sets of participants per course
course_participants = {course: set() for course in courses}

# Read files and populate sets
for file in files:
    # Determine course from filename
    for course in courses:
        if f"_{course}_" in file:
            df = pd.read_csv(file)
            # Combine first and last name to form full name
            df['full_name'] = df['Vorname'].str.strip() + " " + df['Nachname'].str.strip()
            course_participants[course].update(df['full_name'].dropna().unique())
            break

# Compute intersections and Jaccard index
results = []
for r in range(1, len(courses) + 1):
    for combo in itertools.combinations(courses, r):
        sets = [course_participants[c] for c in combo]
        intersection = set.intersection(*sets)
        union = set.union(*sets)
        if len(union) > 0:
            jaccard = len(intersection) / len(union)
            results.append({
                "label": ", ".join(combo),
                "jaccard_index": jaccard
            })

# Create DataFrame
results_df = pd.DataFrame(results)
results_df = results_df.sort_values("jaccard_index", ascending=False)

# Plot
fig = px.bar(results_df, x="label", y="jaccard_index",
             title="Jaccard Index of Participants Across Course Combinations",
             labels={"label": "Course Combination", "jaccard_index": "Jaccard Index"})
fig.update_layout(xaxis_tickangle=-45)
fig.show()
