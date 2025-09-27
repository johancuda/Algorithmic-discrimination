import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Discrimination through data and algorithm", layout="wide")

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
    if gender is not None and gender == "M":
        score +=1
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

st.title("Discrimination through data and algorithm")
container = st.container(border=True)
container.write(
    """Welcome to this interactive experience around algorithmic discrimination, where you can try and create your own risk assessment system to see how algorithms can be biased! This experience is based on various studies around risk assessment systems in the world and gathers identified biases. We specifically base this app around automatic recidivism evaluation, to try and show the different forms of discrimination that could take place in such practices."""
)

st.divider()

########################################

# st.subheader("General informations")

# # sample cards data
# facts = [
#     {"title": "Recidivism score", "text": "The score shown in the profiles underneath mimics the categorization produced by [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri), a tool used by [most German speaking cantons](https://algorithmwatch.ch/en/atlas-db/ros-fall-screening-tool-fast/?text=FaST). It represents three categories, from low chances of recidivism (in blue) to high chances (in red)."},
#     {"title": "The Black-box aspect", "text": "This app mirors the \"Black-box\" aspect that these automated rating systems tend to have. The users (and the inmates being put to evaluations) don't necessarily understand what's going on in the rating process. This problem is notably visible in the FORTES algorithm used by many Swiss Cantons, as shown by [AlgorithmWatch](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/) and Tim Räz in [it's study of FORTES](https://link.springer.com/article/10.1007/s43681-022-00223-y)."},
#     {"title": "Information weight", "text": "All informations don't play the same role in recidivism score calculations. As you can see in the following example, certain variables (e.g. \"Age\") tend to play a greater role than others in the recidivism score. This comes from the architecture of the algorithm used in the evaluation and is thus induced during the construction and programming of the system."},
#     {"title": "Lack of Information", "text": "Missing informations about people doesn't necessarily mean less discrimination. For instance, even though ethnicity or race aren't taken into account when scoring people for recidivism in Swiss systems (such ash [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri) and [FORTES](https://www.mwv-berlin.de/produkte/!/title/fotres--forensisches-operationalisiertes-therapie-risiko-evaluations-system/id/804)), discrimination can still be present through data and practices. Racial profiling is a great example of hidden discrimination hidden in arrest numbers or encounter with the police for a single individual. One could also use ZIP codes to try and infer the ethnicity or origin of a person, using statistics about demographics from certain regions."},
#     {"title": "The Swiss situation", "text": "There is no federal consensus on how to evaluate recidivism risks in Switzerland. The two main systems used are FaST and FOTRES, even though [latin cantons do not use them yet](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine). In [an article from 2018](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine), the SRF points out that these systems lack external evaluation and validation to assess their quality."},
#     {"title": "Chances of recidivism", "text": "There is a misconception about what the chance of recidivism means. For example, when we say that someone has a 43 percent chance of recidivism, it doesn't mean that they will commit another crime 43 percent of the time. It means that from similar profiles, 43 percent of the people have commited another crime."}
#     # Pas sûr de la définition ici!!
# ]

# # init index
# if "idx" not in st.session_state:
#     st.session_state.idx = 0

# def prev_card():
#     st.session_state.idx = max(0, st.session_state.idx - 1)

# def next_card():
#     if st.session_state.idx == len(facts)-1:
#         st.session_state.idx = 0
#     else:
#         st.session_state.idx = min(len(facts) - 1, st.session_state.idx + 1)

# # layout: card area and controls
# col11, col22, col33 = st.columns([1, 6, 1])
# with col11:
#     st.button("← Prev", on_click=prev_card)
# with col33:
#     st.button("Next →", on_click=next_card)

# card = facts[st.session_state.idx]
# with col22:
#     with st.container(border=True):
#         st.markdown(f"### {card['title']}")
#         st.write(card["text"])
#         st.caption(f"{st.session_state.idx + 1} / {len(facts)}")

########################################

st.subheader("How does this experience work ?")

"""
1. Read the texte at the beginning of the "Create your system" section.
2. Click on the different informations you want to include in your system and see how the flagged profiles change. Try different combinations and feel free to read the explanation pop-ups that appear.
3. Try to answer the questions under the "Profiles" section. The answers are available by clicking on the question.
4. (Optional) Check out the resources page to learn more about discimination through algorithms and data.
5. Try the other display by clicking on the link below.
6. Answer the quick survey at the bottom of the page, it would greatly help us.

We hope you'll learn interesting facts about risk assessment systems !
"""

st.page_link("app_user.py", label="Test the first display !", icon="1️⃣")
st.page_link("app_pics.py", label="Test the other display !", icon="2️⃣")

st.divider()

st.subheader("Create your system")

with st.container(border=True):
    "You willl here create your own risk assessment system. You can select the informations you want to use in your system (you can select multiple at once), and you'll see the ratings of the different profiles change accordingly."

col1, col2 = st.columns(2)

with col1:
    st.write("Select what information you want to use in your system:")

    use_gender = st.toggle("Gender", key="use_gender")
    if use_gender:
        st.info("According to the [Swiss Federal Institute of Statistics](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html), men tend to have a higher recidivism rate than women. We don't have any data about other genders.")
    use_ethnicity = st.toggle("Ethnicity", key="use_ethnicity")
    if use_ethnicity:
        st.info("According to [this analysis](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html) by the Swiss Federal Institute of Statistics, non-Swiss people tend to recidivate more.")
    use_encounters = st.toggle("Number of encounters with the police", key="use_encounters")

    if use_encounters:
        st.info("Because police controls can be executed on discriminatory grounds, numbers of encounters with the police can cause discrimination through data. Encounters with the police are defined as any interaction with the police, from roadside checks to police interventions.")

    use_convictions = st.toggle("Number of previous convictions", key="use_convictions")
    if use_convictions:
        st.info("Convictions rate can be influenced by discriminatory decisions, thus influencing the recidivism score.")
    use_age = st.toggle("Age", key="use_age")

    if use_age:
        st.info("According to [this study of the US system **COMPAS**](https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm), younger people tend to be categorized as riskier profiles for recidivism.")


        
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
    max_score = max_possible_score_for_row(row, use_encounters, use_convictions, use_age, use_ethnicity, use_gender)
    percent = 0.0 if max_score == 0 else (score / max_score) * 100.0
    percents.append(round(percent, 1))

df_display = df.copy()
df_display["recidive_score_percent"] = percents

# ---------- Show cards ----------
row1 = st.columns(4)
row2 = st.columns(4)
cards = row1 + row2
nbr_low = 0
nbr_medium = 0
nbr_high = 0

for i, col in enumerate(cards):
    with col.container(border=True):
        c1, c2 = st.columns(2)
        c1.write("**Profile**")
        # Replace with a real image path if you have one
        c1.image(f"{i}.jpg")
        c2.write(f"**Name**: {df_display['name'][i]}")
        c2.write(f"**Age**: {df_display['age'][i]}")
        c2.write(f"**Gender**: {df_display['gender'][i]}")
        c2.write(f"**Ethnicity**: {df_display['ethnicity'][i]}")
        c2.write(f"**Number of convictions**: {df_display['convictions'][i]}")
        c2.write(f"**Number of encounters with the police**: {df_display['encounters'][i]}")

        pct = df_display["recidive_score_percent"][i]
        if pct < 33:
            st.info(f"Recidive score: {pct}%")
            nbr_low += 1
        elif 33 <= pct < 66:
            nbr_medium += 1
            st.warning(f"Recidive score: {pct}%")
        else:
            nbr_high += 1
            st.error(f"Recidive score: {pct}%")


with col2:

    st.info(f"Number of low risk profiles : {nbr_low}")
    st.warning(f"Number of medium risk profiles : {nbr_medium}")
    st.error(f"Number of high risk profiles : {nbr_high}")


st.divider()

st.subheader("Questions")

expander_score = st.expander("What is a recidivism score?")
expander_score.write("""
The score shown in the profiles mimics the categorization produced by [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri), a tool used by [most German speaking cantons](https://algorithmwatch.ch/en/atlas-db/ros-fall-screening-tool-fast/?text=FaST). It represents three categories, from low chances of recidivism (in blue) to high chances (in red).""")

expander_box = st.expander("How does the system work?")
expander_box.write("""
This app mirors the \"black-box\" aspect that these automated rating systems tend to have. The users (and the inmates being put to evaluations) don't necessarily understand what's going on in the rating process. This problem is notably visible in the FORTES algorithm used by many Swiss Cantons, as shown by [AlgorithmWatch](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/) and Tim Räz in [it's study of FORTES](https://link.springer.com/article/10.1007/s43681-022-00223-y).""")

expander_weight = st.expander("Do all the variables have the same impact on the score?")
expander_weight.write("""
All informations don't play the same role in recidivism score calculations. As you can see in the following example, certain variables (e.g. \"Age\") tend to play a greater role than others in the recidivism score. This comes from the architecture of the algorithm used in the evaluation and is thus induced during the construction and programming of the system.""")

expander_missing = st.expander("Could the system be more fair if we removed sensible informations (e.g. gender or ethnicity)?")
expander_missing.write("""
Missing informations about people doesn't necessarily mean less discrimination. For instance, even though ethnicity or race aren't taken into account when scoring people for recidivism in Swiss systems (such ash [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri) and [FORTES](https://www.mwv-berlin.de/produkte/!/title/fotres--forensisches-operationalisiertes-therapie-risiko-evaluations-system/id/804)), discrimination can still be present through data and practices. Racial profiling is a great example of hidden discrimination hidden in arrest numbers or encounter with the police for a single individual. One could also use ZIP codes to try and infer the ethnicity or origin of a person, using statistics about demographics from certain regions.""")

expander_box = st.expander("What is the situation in Switzerland?")
expander_box.write("""
There is no federal consensus on how to evaluate recidivism risks in Switzerland. The two main systems used are FaST and FOTRES, even though [latin cantons do not use them yet](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine). In [an article from 2018](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine), the SRF points out that these systems lack external evaluation and validation to assess their quality. The latin cantons use a system called [PLESORR](https://www.cldjp.ch/plesorr/).""")

# expander_box = st.expander("Are numbers clear?")
# expander_box.write("""
# This app mirors the \"black-box\" aspect that these automated rating systems tend to have. The users (and the inmates being put to evaluations) don't necessarily understand what's going on in the rating process. This problem is notably visible in the FORTES algorithm used by many Swiss Cantons, as shown by [AlgorithmWatch](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/) and Tim Räz in [it's study of FORTES](https://link.springer.com/article/10.1007/s43681-022-00223-y).""")


st.divider()

st.subheader("Survey")

# Streamlit form for input
with st.form(key='app_form'):
    # Form fields (similar to your previous code)
    like = st.text_input("What did you like about this experience ?")
    dislike = st.text_input("What could have been different / better ?")
    offensive = st.checkbox("Did you find the experience with the pictures offensive (check the box if YES)?")

    submit_button = st.form_submit_button("Submit")

    if submit_button:
        if like or dislike or offensive :
            # Authenticate and update the Google Sheet
            client = authenticate_google_sheets()
            form_data = [
                like,dislike, offensive
            ]
            update_google_sheet(form_data)
            st.success("Review successfully submitted, thank you!")
        else:
            st.error("Please fill in all required fields.")