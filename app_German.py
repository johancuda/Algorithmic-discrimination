import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Diskriminierung durch Daten und Algorithmen", layout="wide")

# Function to authenticate and connect to Google Sheets using Streamlit Secrets
def authenticate_google_sheets():
    secrets = st.secrets["google_sheets"]
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
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, 
                                                             ["https://www.googleapis.com/auth/spreadsheets", 
                                                              "https://www.googleapis.com/auth/drive.file"])
    client = gspread.authorize(creds)
    return client

def update_google_sheet(data):
    spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
    sheet = client.open_by_key(spreadsheet_id).sheet1
    sheet.append_row(data)

# ---------- Data ----------
df = pd.DataFrame({
    "name": ["John", "Janine", "Joe", "Jack", "Janet", "Jocelyn", "Leo", "Lara"],
    "age": [21, 18, 36, 98, 45, 63, 28, 24],
    "ethnicity": ["Schweizer", "Andere", "Schweizer", "Andere", "Andere", "Andere", "Andere", "Schweizer"],
    "convictions": [0, 1, 2, 3, 4, 5, 0, 9],
    "encounters": [12, 2, 0, 0, 45, 5, 2, 9],
    "gender": ["M", "F", "N/S", "N/S", "M", "F", "M", "N/S"],
})

# ---------- Scoring logic ----------
def calculate_recidive_score(*, nbr_encounter_police=None, nbr_prior_convictions=None, age=None, gender=None, ethnicity=None):
    score = 0
    if nbr_encounter_police is not None:
        if nbr_encounter_police == 0:
            pass
        elif 0 < nbr_encounter_police < 10:
            score += 1
        elif nbr_encounter_police >= 10:
            score += 2
    if nbr_prior_convictions is not None:
        if nbr_prior_convictions == 1:
            pass
        elif 1 < nbr_prior_convictions < 5:
            score += 1
        elif nbr_prior_convictions >= 5:
            score += 2
    if gender is not None and gender == "M":
        score +=1
    if ethnicity is not None and ethnicity == "Andere":
        if score == 0:
            score = 1
        score *= 1.2
    if age is not None and age < 25:
        if score == 0:
            score = 1 
        score *= 2.5
    return float(score)

def max_possible_score_for_row(row, use_encounters, use_convictions, use_age, use_ethnicity, use_gender):
    worst_encounters = 2 if use_encounters else 0
    worst_convictions = 2 if use_convictions else 0
    worst_gender = 1 if use_gender else 0
    base = worst_encounters + worst_convictions + worst_gender
    if use_age and row["age"] < 25:
        if base == 0:
            base = 1
        base *= 2.5
    if use_ethnicity and row['ethnicity'] == "Andere":
        if base == 0:
            base = 1
        base *= 1.2
    return float(base)

# ---------- UI ----------

st.title("Diskriminierung durch Daten und Algorithmen")
container = st.container(border=True)
container.write(
    """Willkommen zu diesem interaktiven Erlebnis über algorithmische Diskriminierung. 
    Hier können Sie Ihr eigenes Risikobewertungssystem erstellen und sehen, wie Algorithmen voreingenommen sein können! 
    Diese Erfahrung basiert auf verschiedenen Studien über Risikobewertungssysteme weltweit und sammelt bekannte Verzerrungen. 
    Die App konzentriert sich auf automatische Rückfallbewertungen, um verschiedene Formen von Diskriminierung aufzuzeigen, 
    die in solchen Praktiken auftreten können."""
)

st.divider()

st.subheader("Wie funktioniert dieses Erlebnis?")

"""
1. Lesen Sie den Text im Abschnitt „Erstellen Sie Ihr System“.
2. Wählen Sie die Informationen aus, die Sie in Ihr System aufnehmen möchten, und beobachten Sie, wie sich die Profile ändern. Probieren Sie verschiedene Kombinationen aus und lesen Sie die Erklärungs-Pop-ups.
3. Beantworten Sie die Fragen im Abschnitt „Profile“. Die Antworten erscheinen, wenn Sie auf die Fragen klicken.
4. (Optional) Schauen Sie sich die Ressourcenseite an, um mehr über Diskriminierung durch Algorithmen und Daten zu erfahren.
5. Beantworten Sie die kurze Umfrage am Ende der Seite – das hilft uns sehr weiter.

Wir hoffen, dass Sie interessante Fakten über Risikobewertungssysteme lernen!
"""

# st.page_link("app_user.py", label="Testen Sie die erste Ansicht!", icon="1️⃣")
# st.page_link("app_pics.py", label="Testen Sie die andere Ansicht!", icon="2️⃣")

st.divider()

st.subheader("Erstellen Sie Ihr System")

with st.container(border=True):
    "Hier erstellen Sie Ihr eigenes Risikobewertungssystem. Wählen Sie die Informationen aus, die Sie verwenden möchten (mehrere gleichzeitig möglich), und beobachten Sie, wie sich die Bewertungen der Profile ändern."

col1, col2 = st.columns(2)

with col1:
    st.write("Wählen Sie die Informationen, die Sie in Ihrem System verwenden möchten:")

    use_gender = st.toggle("Geschlecht", key="use_gender")
    if use_gender:
        st.info("Laut dem [Bundesamt für Statistik](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html) neigen Männer eher zu Rückfällen als Frauen. Für andere Geschlechter liegen keine Daten vor.")
    use_ethnicity = st.toggle("Ethnizität", key="use_ethnicity")
    if use_ethnicity:
        st.info("Laut [dieser Analyse](https://www.bfs.admin.ch/bfs/fr/home/statistiques/criminalite-droit-penal/recidive/analyses.html) des Bundesamtes für Statistik neigen Nicht-Schweizer häufiger zu Rückfällen.")
    use_encounters = st.toggle("Anzahl Polizeikontakte", key="use_encounters")
    if use_encounters:
        st.info("Da Polizeikontrollen diskriminierend erfolgen können, führen Zahlen zu Polizeikontakten zu Diskriminierung durch Daten. Kontakte umfassen alle Interaktionen, von Verkehrskontrollen bis Polizeieinsätzen.")
    use_convictions = st.toggle("Anzahl früherer Verurteilungen", key="use_convictions")
    if use_convictions:
        st.info("Die Anzahl der Verurteilungen kann durch diskriminierende Entscheidungen beeinflusst sein und so den Rückfall-Score verzerren.")
    use_age = st.toggle("Alter", key="use_age")
    if use_age:
        st.info("Laut [dieser Studie zum US-System **COMPAS**](https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm) werden jüngere Personen tendenziell als riskantere Profile eingestuft.")

st.subheader("Profile")

# ---------- Compute scores ----------
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
    max_score = max_possible_score_for_row(row, use_encounters, use_convictions, use_age, use_ethnicity, use_gender)
    percent = 0.0 if max_score == 0 else (score / max_score) * 100.0
    percents.append(round(percent, 1))

df_display = df.copy()
df_display["rezidiv_score_prozent"] = percents

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
        c2.write(f"**Name**: {df_display['name'][i]}")
        c2.write(f"**Alter**: {df_display['age'][i]}")
        c2.write(f"**Geschlecht**: {df_display['gender'][i]}")
        c2.write(f"**Ethnizität**: {df_display['ethnicity'][i]}")
        c2.write(f"**Anzahl Verurteilungen**: {df_display['convictions'][i]}")
        c2.write(f"**Anzahl Polizeikontakte**: {df_display['encounters'][i]}")

        pct = df_display["rezidiv_score_prozent"][i]
        if pct < 33:
            st.info(f"Rückfall-Score: {pct}%")
            nbr_low += 1
        elif 33 <= pct < 66:
            nbr_medium += 1
            st.warning(f"Rückfall-Score: {pct}%")
        else:
            nbr_high += 1
            st.error(f"Rückfall-Score: {pct}%")

with col2:
    st.info(f"Anzahl Profile mit geringem Risiko: {nbr_low}")
    st.warning(f"Anzahl Profile mit mittlerem Risiko: {nbr_medium}")
    st.error(f"Anzahl Profile mit hohem Risiko: {nbr_high}")

st.divider()

st.subheader("Fragen")

expander_score = st.expander("Was ist ein Rückfall-Score?")
expander_score.write("""
Der in den Profilen angezeigte Score imitiert die Kategorisierung von [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri), einem Tool, das in den [meisten deutschsprachigen Kantonen](https://algorithmwatch.ch/en/atlas-db/ros-fall-screening-tool-fast/?text=FaST) verwendet wird. Er repräsentiert drei Kategorien, von geringer Rückfallgefahr (blau) bis hoher Rückfallgefahr (rot).""")

expander_box = st.expander("Wie funktioniert das System?")
expander_box.write("""
Diese App spiegelt den „Black-Box“-Charakter wider, den viele automatisierte Bewertungssysteme haben. 
Die Nutzer (und die Bewerteten) verstehen oft nicht, wie die Einstufung zustande kommt. 
Dieses Problem ist besonders im Algorithmus FOTRES sichtbar, der in vielen Schweizer Kantonen genutzt wird, wie [AlgorithmWatch](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/) 
und Tim Räz in [seiner Studie](https://link.springer.com/article/10.1007/s43681-022-00223-y) zeigen.""")

expander_weight = st.expander("Haben alle Variablen den gleichen Einfluss?")
expander_weight.write("""
Nicht alle Informationen spielen dieselbe Rolle bei der Berechnung des Rückfall-Scores. 
Bestimmte Variablen (z. B. „Alter“) haben ein größeres Gewicht als andere. 
Das ergibt sich aus der Architektur des Algorithmus und wird durch die Programmierung vorgegeben.""")

expander_missing = st.expander("Wäre das System fairer, wenn sensible Informationen (z. B. Geschlecht oder Ethnizität) weggelassen würden?")
expander_missing.write("""
Fehlende Informationen über Personen bedeuten nicht unbedingt weniger Diskriminierung. 
Auch wenn Ethnizität oder Herkunft in Schweizer Systemen wie [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri) und [FOTRES](https://www.mwv-berlin.de/produkte/!/title/fotres--forensisches-operationalisiertes-therapie-risiko-evaluations-system/id/804) 
nicht berücksichtigt werden, kann Diskriminierung durch Daten und Praktiken dennoch auftreten. 
Racial Profiling ist ein gutes Beispiel für versteckte Diskriminierung, die sich in Verhaftungszahlen oder Polizeikontakten zeigt. 
Auch Postleitzahlen könnten genutzt werden, um indirekt die Herkunft zu erschließen.""")

expander_box = st.expander("Wie ist die Situation in der Schweiz?")
expander_box.write("""
Es gibt keinen eidgenössischen Konsens darüber, wie Rückfallrisiken bewertet werden sollen. 
Die beiden Hauptsysteme sind FaST und FOTRES, während [lateinische Kantone sie noch nicht nutzen](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine). 
[Ein Artikel von 2018](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine) der SRF weist darauf hin, dass diesen Systemen externe Evaluationen und Qualitätsprüfungen fehlen. 
In den lateinischen Kantonen wird ein System namens [PLESORR](https://www.cldjp.ch/plesorr/) verwendet.""")

st.divider()

st.subheader("Umfrage")

with st.form(key='app_form'):
    like = st.text_input("Was hat Ihnen an diesem Erlebnis gefallen?")
    dislike = st.text_input("Was hätte anders / besser sein können?")
    offensive = st.checkbox("Fanden Sie die Erfahrung mit den Bildern anstößig (ankreuzen, wenn JA)?")

    submit_button = st.form_submit_button("Absenden")

    if submit_button:
        if like or dislike or offensive :
            client = authenticate_google_sheets()
            form_data = [like,dislike, offensive]
            update_google_sheet(form_data)
            st.success("Feedback erfolgreich übermittelt, vielen Dank!")
        else:
            st.error("Bitte füllen Sie alle erforderlichen Felder aus.")
