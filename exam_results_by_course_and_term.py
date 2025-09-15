# AI GENERATED

import pandas as pd
import plotly.express as px

# Load CSV and strip column names
df = pd.read_csv("data/passed_exam_by_coures.csv")
df.columns = df.columns.str.strip()  # remove hidden spaces

# Clean whitespace in numbers
df['num_passed'] = df['num_passed'].astype(str).str.strip().astype(int)
df['num_failed'] = df['num_failed'].astype(str).str.strip().astype(int)

# Melt for stacking
df_long = df.melt(
    id_vars=['term', 'course'],
    value_vars=['num_passed', 'num_failed'],
    var_name='Result',
    value_name='Count'
)

# Map nicer labels
df_long['Result'] = df_long['Result'].map({
    'num_passed': 'Passed',
    'num_failed': 'Failed'
})

# Plot stacked bars per course, custom order
fig = px.bar(
    df_long,
    x='term',
    y='Count',
    color='Result',
    barmode='stack',
    facet_col='course',
    category_orders={
        'term': sorted(df['term'].unique()), 
        'course': ['ML1', 'ML2', 'DL2', 'AML', 'AMLS']  # custom order
    },
    title='Exam Results by Course and Term'
)

fig.update_layout(showlegend=True)
fig.show()
