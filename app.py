""" Streamlit app to showcase discriminations"""

import streamlit as st

import pandas as pd

df = pd.DataFrame({
    "name": ["john", "jack", "joe", "janine", "janet", "jocelyn"],
    "age": [21, 12, 36, 98, 45, 63],
    "ethnicity": ["caucasian", "latino", "latino", "latino", "caucasian", "caucasian"],
    "convictions": [0,1,2,3,4,5],
    "encounters": [12,2,0,0,45,5],
    "gender" : ["m", "f","m", "f","m", "f"]
})

def calculate_recidive_score(**kwargs):
    score = 0
    
    nbr_encounter_police = kwargs.get("nbr_encounter_police")
    nbr_prior_convictions = kwargs.get("nbr_prior_convictions")
    age = kwargs.get("age")
    gender = kwargs.get("gender")       # not used yet
    ethnicity = kwargs.get("ethnicity") # not used yet

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

    # Age
    if age is not None and age < 25:
        score *= 2.5

    return score

df['recidive_score'] = [calculate_recidive_score(gender=gender, ethnicity=ethnicity, nbr_encounter_police=nbr_encounter_police, nbr_prior_convictions=nbr_prior_convictions, age=age) for gender, ethnicity, nbr_encounter_police, nbr_prior_convictions, age in zip(df['gender'],
        df['ethnicity'],
        df['encounters'],
        df['convictions'],
        df['age'])]

st.title("Discrimination through data and algorithm")

container = st.container(border=True)

container.write("Welcome to this interactive experience around algorithmic discrimination, where you can try and create your own risk assessment system to see how algorithms can be biased!")

st.write("Select what informations you want to use in your system : ")

gender = st.checkbox("Gender")

ethnicity = st.checkbox("Ethnicity")

nbr_encounter_police = st.checkbox("Number of encounters with the police")

nbr_prior_convictions = st.checkbox("Number of previous convictions")

age = st.checkbox("Age")

st.divider()

st.subheader("Profiles")

row1 = st.columns(3)
row2 = st.columns(3)

i = 0
for col in row1 + row2:
    with col.container(border=True):
        col1, col2 = st.columns(2)
        col1.write(f"Profile number")
        col1.image("https://i.sstatic.net/HQwHI.jpg")
        col2.write(f"Name: {df['name'][i]}")
        col2.write(f"Age: {df['age'][i]}")
        col2.write(f"Ethnicity: {df['ethnicity'][i]}")
        col2.write(f"Number of convictions: {df['convictions'][i]}")
        col2.write(f"Number of encounters with the police: {df['encounters'][i]}")
        if df['recidive_score'][i] < 33:
            st.info(f"Recidive score : {df['recidive_score'][i]}%")
        elif 33< df['recidive_score'][i] < 66:
            st.warning(f"Recidive score : {df['recidive_score'][i]}%")
        elif df['recidive_score'][i] > 66:
            st.error(f"Recidive score : {df['recidive_score'][i]}%")

        i += 1




    

    