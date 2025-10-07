import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Discrimination through Data and Algorithms", layout="wide")

# Function to authenticate and connect to Google Sheets using Streamlit Secrets
def authenticate_google_sheets():
    # Load credentials from Streamlit Secrets
    secrets = st.secrets["google_sheets"]
    
    # Prepare the credentials for authentication
    credentials = {
        "type": "service_account",
        "project_id": secrets["project_id"],
        "private_key_id": secrets["private_key_id"],
        "private_key": secrets["private_key"].replace("\\n", "\n"),
        "client_email": secrets["client_email"],
        "client_id": secrets["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": secrets["client_x509_cert_url"]
    }
    
    # Convert the credentials to a format suitable for gspread
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, 
                                                             ["https://www.googleapis.com/auth/spreadsheets", 
                                                              "https://www.googleapis.com/auth/drive.file"])
    client = gspread.authorize(creds)
    return client

# Function to update the Google Sheet with form data
def update_google_sheet(data):
    # Use Streamlit Secrets to get the spreadsheet ID
    spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
    
    # Open the Google Sheet by ID
    sheet = client.open_by_key(spreadsheet_id).sheet1  # Assuming sheet1 is the target sheet
    sheet.append_row(data)  # Add the form data as a new row

# ---------- Data ----------
df = pd.DataFrame({
    "name": ["John", "Janine", "Joe", "Jack", "Janet", "Jocelyn", "Leo", "Lara"],
    "age": [21, 18, 36, 98, 45, 63, 28, 24],
    "ethnicity": ["Swiss", "Other", "Swiss", "Other", "Other", "Other", "Other", "Swiss"],
    "convictions": [0, 1, 2, 3, 4, 5, 0, 9],
    "encounters": [12, 2, 0, 0, 45, 5, 2, 9],
    "gender": ["M", "F", "N/S", "N/S", "M", "F", "M", "N/S"],
})

# ---------- Scoring logic ----------
def calculate_recidivism_score(*, nbr_encounter_police=None, nbr_prior_convictions=None, age=None, gender=None, ethnicity=None):
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

    if gender is not None and gender == "M":
        score += 1

    if ethnicity is not None and ethnicity == "Other":
        if score == 0:
            score = 1
        score *= 1.2

    # Age multiplier
    if age is not None and age < 25:
        if score == 0:
            score = 1 
        score *= 2.5

    return float(score)

def max_possible_score_for_row(row, use_encounters, use_convictions, use_age, use_ethnicity, use_gender):
    # Worst-case inputs for enabled features, keeping the person's actual age for the age rule
    worst_encounters = 2 if use_encounters else 0
    worst_convictions = 2 if use_convictions else 0
    worst_gender = 1 if use_gender else 0
    base = worst_encounters + worst_convictions + worst_gender
    if use_age and row["age"] < 25:
        if base == 0:
            base = 1
        base *= 2.5
    if use_ethnicity and row['ethnicity'] == "Other":
        if base == 0:
            base = 1
        base *= 1.2
    return float(base)

# ---------- UI ----------

st.title("Discrimination through Data and Algorithms")
container = st.container(border=True)
container.write(
    """Welcome to this interactive experience about algorithmic discrimination. Here, you can design your own risk assessment system to explore how algorithms can reproduce or amplify bias. This experience is based on various studies on global risk assessment systems and illustrates common biases identified in such tools. It focuses on automated recidivism evaluation to highlight the different forms of discrimination that may occur in these practices."""
)

st.divider()

st.subheader("How does this experience work?")

"""
1. Read the text at the beginning of the “Create your system” section.
2. Click on the different types of information you want to include in your system and observe how the profiles’ scores change. Try different combinations and read the explanation pop-ups that appear.
3. Try to answer the questions under the “Profiles” section. Answers can be revealed by clicking on each question.
4. (Optional) Visit the resources page to learn more about discrimination through algorithms and data.
5. Answer the quick survey at the bottom of the page — your feedback helps us improve.

We hope you’ll gain valuable insights about risk assessment systems!
"""

st.divider()

st.subheader("Create your system")

with st.container(border=True):
    "Here, you can create your own risk assessment system. Select the information you want to use (you can choose several options), and observe how the risk ratings of the profiles change accordingly."

col1, col2 = st.columns(2)

with col1:
    st.write("Select which information you want to include in your system:")

    use_gender = st.toggle("Gender", key="use_gender")
    if use_gender:
        st.info("According to the [Swiss Federal Statistical Office](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html), men tend to have a higher recidivism rate than women. No data is currently available for other genders.")

    use_ethnicity = st.toggle("Ethnicity", key="use_ethnicity")
    if use_ethnicity:
        st.info("According to [this analysis](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html) by the Swiss Federal Statistical Office, non-Swiss individuals tend to reoffend more often.")

    use_encounters = st.toggle("Number of encounters with the police", key="use_encounters")
    if use_encounters:
        st.info("Since police checks can be performed on discriminatory grounds, the number of encounters with the police can reflect bias in data. ‘Encounters’ include any interaction with the police, from roadside checks to interventions.")

    use_convictions = st.toggle("Number of previous convictions", key="use_convictions")
    if use_convictions:
        st.info("Conviction rates may be influenced by systemic biases, thus affecting the recidivism score.")

    use_age = st.toggle("Age", key="use_age")
    if use_age:
        st.info("According to [this study on the US COMPAS system](https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm), younger individuals are often categorized as higher-risk profiles for recidivism.")

st.subheader("Profiles")

# ---------- Compute scores dynamically ----------
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

    score = calculate_recidivism_score(**kwargs)
    scores.append(score)

    max_score = max_possible_score_for_row(row, use_encounters, use_convictions, use_age, use_ethnicity, use_gender)
    percent = 0.0 if max_score == 0 else (score / max_score) * 100.0
    percents.append(round(percent, 1))

df_display = df.copy()
df_display["recidivism_score_percent"] = percents

# ---------- Show cards ----------
row1 = st.columns(4)
row2 = st.columns(4)
cards = row1 + row2
nbr_low, nbr_medium, nbr_high = 0, 0, 0

for i, col in enumerate(cards):
    with col.container(border=True):
        c1, c2 = st.columns(2)
        c1.write("**Profile**")
        c1.image("assets/img/user.png")
        c2.write(f"**Name:** {df_display['name'][i]}")
        c2.write(f"**Age:** {df_display['age'][i]}")
        c2.write(f"**Gender:** {df_display['gender'][i]}")
        c2.write(f"**Ethnicity:** {df_display['ethnicity'][i]}")
        c2.write(f"**Number of convictions:** {df_display['convictions'][i]}")
        c2.write(f"**Number of police encounters:** {df_display['encounters'][i]}")

        pct = df_display["recidivism_score_percent"][i]
        if pct < 33:
            st.info(f"Recidivism score: {pct}%")
            nbr_low += 1
        elif 33 <= pct < 66:
            nbr_medium += 1
            st.warning(f"Recidivism score: {pct}%")
        else:
            nbr_high += 1
            st.error(f"Recidivism score: {pct}%")

with col2:
    st.info(f"Number of low-risk profiles: {nbr_low}")
    st.warning(f"Number of medium-risk profiles: {nbr_medium}")
    st.error(f"Number of high-risk profiles: {nbr_high}")

st.divider()

st.subheader("Questions")

expander_score = st.expander("What is a recidivism score?")
expander_score.write("""
The score shown in the profiles mimics the categorization produced by [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri), a tool used by [most German-speaking cantons](https://algorithmwatch.ch/en/atlas-db/ros-fall-screening-tool-fast/?text=FaST). It represents three categories, from low chances of recidivism (in blue) to high chances (in red).
""")

expander_box = st.expander("How does the system work?")
expander_box.write("""
This app mirrors the “black-box” nature of automated rating systems. Users (and the individuals being evaluated) often don’t understand what happens during the scoring process. This opacity is notably present in the FOTRES algorithm used by several Swiss cantons, as shown by [AlgorithmWatch](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/) and Tim Räz in [his study on FOTRES](https://link.springer.com/article/10.1007/s43681-022-00223-y).
""")

expander_weight = st.expander("Do all variables have the same impact on the score?")
expander_weight.write("""
Not all pieces of information contribute equally to recidivism score calculations. Some variables (e.g., “Age”) tend to have a greater influence. This stems from the algorithm’s design and the choices made during its construction and programming.
""")

expander_missing = st.expander("Would removing sensitive information (e.g., gender or ethnicity) make the system fairer?")
expander_missing.write("""
Removing sensitive data does not necessarily reduce discrimination. For instance, even though ethnicity or race are not explicitly included in Swiss recidivism scoring systems such as [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri) and [FOTRES](https://www.mwv-berlin.de/produkte/!/title/fotres--forensisches-operationalisiertes-therapie-risiko-evaluations-system/id/804), bias can still emerge through correlated data or practices. Racial profiling, for example, can introduce hidden discrimination via arrest rates or police encounters. Similarly, ZIP codes can indirectly reveal a person’s origin or ethnicity based on demographic data.
""")

expander_box = st.expander("What is the situation in Switzerland?")
expander_box.write("""
There is no federal consensus on how to evaluate recidivism risks in Switzerland. The two main systems used are FaST and FOTRES, although [French-speaking cantons do not yet use them](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine). According to [a 2018 SRF article](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine), these systems lack external evaluation and validation. French-speaking cantons use a system called [PLESORR](https://www.cldjp.ch/plesorr/). For a broader overview of automated systems in Switzerland, consult [this report](https://automatingsociety.algorithmwatch.org/wp-content/uploads/2021/01/Automating-Society-Report-2020-CH-Edition-DE-FR-IT-EN.pdf).
""")

st.divider()

st.subheader("Survey")

with st.form(key='app_form'):
    like = st.text_input("What did you like about this experience?")
    dislike = st.text_input("What could have been improved?")
    offensive = st.checkbox("Did you find any part of this experience offensive (check the box if YES)?")

    submit_button = st.form_submit_button("Submit")

    if submit_button:
        if like or dislike or offensive:
            client = authenticate_google_sheets()
            form_data = [like, dislike, offensive]
            update_google_sheet(form_data)
            st.success("Review successfully submitted. Thank you for your feedback!")
        else:
            st.error("Please fill in at least one field before submitting.")
