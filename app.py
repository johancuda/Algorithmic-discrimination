import streamlit as st
import pandas as pd

st.set_page_config(page_title="Discrimination through data and algorithm", layout="wide")

# ---------- Data ----------
df = pd.DataFrame({
    "name": ["john", "jack", "joe", "janine", "janet", "jocelyn"],
    "age": [21, 12, 36, 98, 45, 63],
    "ethnicity": ["caucasian", "latino", "latino", "latino", "caucasian", "caucasian"],
    "convictions": [0, 1, 2, 3, 4, 5],
    "encounters": [12, 2, 0, 0, 45, 5],
    "gender": ["m", "f", "m", "f", "m", "f"],
})

# ---------- Scoring logic (same as yours, kept simple) ----------
def calculate_recidive_score(*, nbr_encounter_police=None, nbr_prior_convictions=None, age=None, gender=None, ethnicity=None):
    score = 0

    # Encounters with police
    if nbr_encounter_police is not None:
        if nbr_encounter_police == 0:
            pass
        elif 0 < nbr_encounter_police < 10:
            score += 1
        elif nbr_encounter_police >= 10:
            score += 2

    # Prior convictions
    if nbr_prior_convictions is not None:
        if nbr_prior_convictions == 1:
            pass
        elif 1 < nbr_prior_convictions < 5:
            score += 1
        elif nbr_prior_convictions >= 5:
            score += 2

    # Age multiplier
    if age is not None and age < 25:
        if score == 0:
            score = 1 
        score *= 2.5

    return float(score)

def max_possible_score_for_row(row, use_encounters, use_convictions, use_age):
    # Worst-case inputs for enabled features, keeping the person's actual age for the age rule
    worst_encounters = 2 if use_encounters else 0
    worst_convictions = 2 if use_convictions else 0
    base = worst_encounters + worst_convictions
    if use_age and row["age"] < 25:
        if base == 0:
            base = 1
        base *= 2.5
    return float(base)

# ---------- UI ----------

st.title("Discrimination through data and algorithm")
container = st.container(border=True)
container.write(
    "Welcome to this interactive experience around algorithmic discrimination, "
    "where you can try and create your own risk assessment system to see how algorithms can be biased!"
    " This experience is based on various studies around risk assessment systems in the world and gathers identified biases."
)

col1, col2 = st.columns([0.3,0.7])

with col1:

    st.write("Select what information you want to use in your system:")

    use_gender = st.toggle("Gender", key="use_gender")
    use_ethnicity = st.toggle("Ethnicity", key="use_ethnicity")
    use_encounters = st.toggle("Number of encounters with the police", key="use_encounters")

    if use_encounters:
        st.info("Because of racial profiling, numbers of encounters with the police can cause discrimination.")

    use_convictions = st.toggle("Number of previous convictions", key="use_convictions")
    use_age = st.toggle("Age", key="use_age")

    if use_age:
        st.info("According to [this study of the US system **COMPAS**](https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm), younger people tend to be categorized as riskier profiles for recidivism.")


with col2:
        
    st.subheader("Profiles")

    # ---------- Compute scores dynamically on every rerun ----------
    scores = []
    percents = []
    for _, row in df.iterrows():
        kwargs = {}
        if use_gender:
            kwargs["gender"] = row["gender"]
        if use_ethnicity:
            kwargs["ethnicity"] = row["ethnicity"]
        if use_encounters:
            kwargs["nbr_encounter_police"] = row["encounters"]
        if use_convictions:
            kwargs["nbr_prior_convictions"] = row["convictions"]
        if use_age:
            kwargs["age"] = row["age"]

        score = calculate_recidive_score(**kwargs)
        scores.append(score)

        # Convert to percent relative to this profile's max possible given current toggles
        max_score = max_possible_score_for_row(row, use_encounters, use_convictions, use_age)
        percent = 0.0 if max_score == 0 else (score / max_score) * 100.0
        percents.append(round(percent, 1))

    df_display = df.copy()
    df_display["recidive_score_percent"] = percents

    # ---------- Show cards ----------
    row1 = st.columns(3)
    row2 = st.columns(3)
    cards = row1 + row2

    for i, col in enumerate(cards):
        with col.container(border=True):
            c1, c2 = st.columns(2)
            c1.write("**Profile**")
            # Replace with a real image path if you have one
            c1.image("pic.jpg")
            c2.write(f"**Name**: {df_display['name'][i]}")
            c2.write(f"**Age**: {df_display['age'][i]}")
            c2.write(f"**Gender**: {df_display['gender'][i]}")
            c2.write(f"**Ethnicity**: {df_display['ethnicity'][i]}")
            c2.write(f"**Number of convictions**: {df_display['convictions'][i]}")
            c2.write(f"**Number of encounters with the police**: {df_display['encounters'][i]}")

            pct = df_display["recidive_score_percent"][i]
            if pct < 33:
                st.info(f"Recidive score: {pct}%")
            elif 33 <= pct < 66:
                st.warning(f"Recidive score: {pct}%")
            else:
                st.error(f"Recidive score: {pct}%")
