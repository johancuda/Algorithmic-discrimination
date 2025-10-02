import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Discrimination par les données et les algorithmes", layout="wide")

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

st.title("Discrimination par les données et les algorithmes")
container = st.container(border=True)
container.write(
    """Bienvenue dans cette expérience interactive autour de la discrimination algorithmique, où vous pouvez essayer de créer votre propre système d’évaluation du risque afin de voir comment les algorithmes peuvent être biaisés ! 
Cette expérience s’inspire de différentes études sur les systèmes d’évaluation du risque dans le monde et rassemble les biais identifiés. 
Nous basons spécifiquement cette application sur l’évaluation automatique du risque de récidive, pour montrer les différentes formes de discrimination possibles dans de telles pratiques."""
)

st.divider()

st.subheader("Comment fonctionne cette expérience ?")

"""
1. Lisez le texte au début de la section « Créez votre système ».
2. Cliquez sur les différentes informations que vous souhaitez inclure dans votre système et observez comment les profils changent. Essayez différentes combinaisons et n’hésitez pas à lire les explications qui apparaissent.
3. Essayez de répondre aux questions sous la section « Profils ». Les réponses sont disponibles en cliquant sur les questions.
4. (Optionnel) Consultez la page de ressources pour en apprendre davantage sur la discrimination par les algorithmes et les données.
5. Répondez au rapide sondage en bas de la page, cela nous aidera beaucoup.

Nous espérons que vous apprendrez des éléments intéressants sur les systèmes d’évaluation du risque !
"""

# st.page_link("app_user.py", label="Tester le premier affichage !", icon="1️⃣")
# st.page_link("app_pics.py", label="Tester l’autre affichage !", icon="2️⃣")

st.divider()

st.subheader("Créez votre système")

with st.container(border=True):
    "Vous allez ici créer votre propre système d’évaluation du risque. Vous pouvez sélectionner les informations que vous souhaitez utiliser (plusieurs choix possibles) et vous verrez les évaluations des profils changer en conséquence."

col1, col2 = st.columns(2)

with col1:
    st.write("Sélectionnez les informations que vous souhaitez utiliser dans votre système :")

    use_gender = st.toggle("Genre", key="use_gender")
    if use_gender:
        st.info("Selon [l’Office fédéral de la statistique](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html), les hommes ont tendance à présenter un taux de récidive plus élevé que les femmes. Nous n’avons pas de données concernant les autres genres.")
    use_ethnicity = st.toggle("Origine / nationalité", key="use_ethnicity")
    if use_ethnicity:
        st.info("Selon [cette analyse](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html) de l’Office fédéral de la statistique, les personnes non suisses ont tendance à récidiver davantage.")
    use_encounters = st.toggle("Nombre de rencontres avec la police", key="use_encounters")
    if use_encounters:
        st.info("Comme les contrôles de police peuvent être effectués sur des bases discriminatoires, le nombre de rencontres avec la police peut induire de la discrimination via les données. Les rencontres incluent toute interaction avec la police, des contrôles routiers aux interventions policières.")
    use_convictions = st.toggle("Nombre de condamnations antérieures", key="use_convictions")
    if use_convictions:
        st.info("Le taux de condamnations peut être influencé par des décisions discriminatoires, ce qui impacte le score de récidive.")
    use_age = st.toggle("Âge", key="use_age")
    if use_age:
        st.info("Selon [cette étude sur le système américain **COMPAS**](https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm), les personnes plus jeunes sont souvent considérées comme présentant un risque plus élevé de récidive.")

st.subheader("Profils")

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
        c1.write("**Profil**")
        c1.image(f"assets/img/user.png")
        c2.write(f"**Nom**: {df_display['name'][i]}")
        c2.write(f"**Âge**: {df_display['age'][i]}")
        c2.write(f"**Genre**: {df_display['gender'][i]}")
        c2.write(f"**Origine / nationalité**: {df_display['ethnicity'][i]}")
        c2.write(f"**Nombre de condamnations**: {df_display['convictions'][i]}")
        c2.write(f"**Nombre de rencontres avec la police**: {df_display['encounters'][i]}")

        pct = df_display["recidive_score_percent"][i]
        if pct < 33:
            nbr_low += 1
            st.info(f"Score de récidive : {pct}%")
        elif 33 <= pct < 66:
            nbr_medium += 1
            st.warning(f"Score de récidive : {pct}%")
        else:
            nbr_high += 1
            st.error(f"Score de récidive : {pct}%")

with col2:
    st.info(f"Nombre de profils à faible risque : {nbr_low}")
    st.warning(f"Nombre de profils à risque moyen : {nbr_medium}")
    st.error(f"Nombre de profils à risque élevé : {nbr_high}")

st.divider()

st.subheader("Questions")

expander_score = st.expander("Qu’est-ce qu’un score de récidive ?")
expander_score.write("""
Le score affiché dans les profils imite la catégorisation produite par [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri), un outil utilisé par [la plupart des cantons alémaniques](https://algorithmwatch.ch/en/atlas-db/ros-fall-screening-tool-fast/?text=FaST). 
Il représente trois catégories, allant de faibles chances de récidive (en bleu) à de fortes chances (en rouge).""")

expander_box = st.expander("Comment fonctionne le système ?")
expander_box.write("""
Cette application reflète l’aspect de « boîte noire » que ces systèmes de notation automatisés ont souvent. 
Les utilisateurs (et les personnes évaluées) ne comprennent pas nécessairement le processus de notation. 
Ce problème est particulièrement visible avec l’algorithme FOTRES, utilisé dans de nombreux cantons suisses, comme le montrent [AlgorithmWatch](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/) et l’étude de Tim Räz [à ce sujet](https://link.springer.com/article/10.1007/s43681-022-00223-y).""")

expander_weight = st.expander("Toutes les variables ont-elles le même impact sur le score ?")
expander_weight.write("""
Toutes les informations ne jouent pas le même rôle dans le calcul du score de récidive. 
Par exemple, certaines variables (comme l’« âge ») pèsent plus lourd que d’autres. 
Cela provient de l’architecture de l’algorithme utilisé pour l’évaluation, et donc de sa construction et programmation.""")

expander_missing = st.expander("Le système serait-il plus juste si l’on supprimait certaines informations sensibles (genre, origine, etc.) ?")
expander_missing.write("""
Le fait de supprimer certaines informations ne signifie pas nécessairement moins de discrimination. 
Par exemple, même si l’origine ou l’ethnicité ne sont pas prises en compte dans les systèmes suisses (comme [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri) ou [FOTRES](https://www.mwv-berlin.de/produkte/!/title/fotres--forensisches-operationalisiertes-therapie-risiko-evaluations-system/id/804)), la discrimination peut être présente via les données et les pratiques. 
Le profilage racial est un bon exemple : il influence les statistiques d’arrestations ou de contrôles de police. On peut aussi utiliser le code postal pour déduire indirectement l’origine d’une personne via des statistiques démographiques régionales.""")

expander_box = st.expander("Quelle est la situation en Suisse ?")
expander_box.write("""
Il n’existe pas de consensus fédéral sur la manière d’évaluer le risque de récidive en Suisse. 
Les deux principaux systèmes utilisés sont FaST et FOTRES, bien que [les cantons latins ne les utilisent pas encore](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine). 
Dans [un article de 2018](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine), la SRF souligne que ces systèmes manquent d’évaluations externes et de validations pour juger de leur qualité. 
Les cantons latins utilisent un système appelé [PLESORR](https://www.cldjp.ch/plesorr/). Si vous souhaitez une vue plus générale des systèmes automatisés en Suisse, lisez [ce rapport](https://automatingsociety.algorithmwatch.org/wp-content/uploads/2021/01/Automating-Society-Report-2020-CH-Edition-DE-FR-IT-EN.pdf).""")

st.divider()

st.subheader("Sondage")

with st.form(key='app_form'):
    like = st.text_input("Qu’avez-vous apprécié dans cette expérience ?")
    dislike = st.text_input("Qu’est-ce qui aurait pu être différent / meilleur ?")
    offensive = st.checkbox("Avez-vous trouvé l’expérience avec les images offensante (cochez si OUI) ?")

    submit_button = st.form_submit_button("Envoyer")

    if submit_button:
        if like or dislike or offensive :
            client = authenticate_google_sheets()
            form_data = [like, dislike, offensive]
            update_google_sheet(form_data)
            st.success("Avis envoyé avec succès, merci !")
        else:
            st.error("Veuillez remplir tous les champs obligatoires.")
