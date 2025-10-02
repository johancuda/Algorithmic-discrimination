import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


st.set_page_config(page_title="Discriminazione tramite dati e algoritmi", layout="wide")

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

st.title("Discriminazione tramite dati e algoritmi")
container = st.container(border=True)
container.write(
    """Benvenuti in questa esperienza interattiva sulla discriminazione algoritmica, 
dove potete provare a creare il vostro sistema di valutazione del rischio per vedere 
come gli algoritmi possano essere distorti! 
Questa esperienza si ispira a diversi studi sui sistemi di valutazione del rischio nel mondo 
e riunisce i pregiudizi identificati. 
Basiamo specificamente questa applicazione sulla valutazione automatica del rischio di recidiva, 
per mostrare le diverse forme di discriminazione possibili in tali pratiche."""
)

st.divider()

st.subheader("Come funziona questa esperienza?")

"""
1. Leggete il testo all’inizio della sezione «Create il vostro sistema».
2. Cliccate sulle diverse informazioni che volete includere nel vostro sistema e osservate come cambiano i profili. Provate diverse combinazioni e non esitate a leggere le spiegazioni che compaiono.
3. Cercate di rispondere alle domande nella sezione «Profili». Le risposte sono disponibili cliccando sulle domande.
4. (Opzionale) Consultate la pagina delle risorse per saperne di più sulla discriminazione tramite algoritmi e dati.
5. Rispondete al breve sondaggio in fondo alla pagina, ci aiuterà molto.

Speriamo che possiate imparare qualcosa di interessante sui sistemi di valutazione del rischio!
"""

st.divider()

st.subheader("Create il vostro sistema")

with st.container(border=True):
    "Qui creerete il vostro sistema di valutazione del rischio. Potete selezionare le informazioni che volete usare (anche più di una) e vedrete cambiare le valutazioni dei profili di conseguenza."

col1, col2 = st.columns(2)

with col1:
    st.write("Selezionate le informazioni che volete usare nel vostro sistema:")

    use_gender = st.toggle("Genere", key="use_gender")
    if use_gender:
        st.info("Secondo [l’Ufficio federale di statistica](https://www.bfs.admin.ch/bfs/it/home/statistiche/criminalita-diritto-penale/recidiva/analisi.html), gli uomini tendono ad avere un tasso di recidiva più elevato rispetto alle donne. Non abbiamo dati sugli altri generi.")
    use_ethnicity = st.toggle("Origine / nazionalità", key="use_ethnicity")
    if use_ethnicity:
        st.info("Secondo [questa analisi](https://www.bfs.admin.ch/bfs/it/home/statistiche/criminalita-diritto-penale/recidiva/analisi.html) dell’Ufficio federale di statistica, le persone non svizzere tendono a recidivare di più.")
    use_encounters = st.toggle("Numero di incontri con la polizia", key="use_encounters")
    if use_encounters:
        st.info("Poiché i controlli di polizia possono essere effettuati su basi discriminatorie, il numero di incontri con la polizia può introdurre discriminazione attraverso i dati. Gli incontri includono qualsiasi interazione con la polizia, dai controlli stradali agli interventi.")
    use_convictions = st.toggle("Numero di condanne precedenti", key="use_convictions")
    if use_convictions:
        st.info("Il numero di condanne può essere influenzato da decisioni discriminatorie, con un impatto sul punteggio di recidiva.")
    use_age = st.toggle("Età", key="use_age")
    if use_age:
        st.info("Secondo [questo studio sul sistema americano **COMPAS**](https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm), le persone più giovani sono spesso considerate a rischio più elevato di recidiva.")

st.subheader("Profili")

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

# ---------- Cards ----------
for i, col in enumerate(cards):
    with col.container(border=True):
        c1, c2 = st.columns(2)
        c1.write("**Profilo**")
        c1.image(f"assets/img/user.png")
        c2.write(f"**Nome**: {df_display['name'][i]}")
        c2.write(f"**Età**: {df_display['age'][i]}")
        c2.write(f"**Genere**: {df_display['gender'][i]}")
        c2.write(f"**Origine / nazionalità**: {df_display['ethnicity'][i]}")
        c2.write(f"**Numero di condanne**: {df_display['convictions'][i]}")
        c2.write(f"**Numero di incontri con la polizia**: {df_display['encounters'][i]}")

        pct = df_display["recidive_score_percent"][i]
        if pct < 33:
            nbr_low += 1
            st.info(f"Punteggio di recidiva: {pct}%")
        elif 33 <= pct < 66:
            nbr_medium += 1
            st.warning(f"Punteggio di recidiva: {pct}%")
        else:
            nbr_high += 1
            st.error(f"Punteggio di recidiva: {pct}%")

with col2:
    st.info(f"Numero di profili a basso rischio: {nbr_low}")
    st.warning(f"Numero di profili a rischio medio: {nbr_medium}")
    st.error(f"Numero di profili ad alto rischio: {nbr_high}")

st.divider()

st.subheader("Domande")

expander_score = st.expander("Che cos’è un punteggio di recidiva?")
expander_score.write("""
Il punteggio mostrato nei profili imita la categorizzazione prodotta da [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri), uno strumento usato dalla maggior parte dei cantoni svizzero-tedeschi. 
Rappresenta tre categorie, da basse probabilità di recidiva (in blu) ad alte probabilità (in rosso).""")

expander_box = st.expander("Come funziona il sistema?")
expander_box.write("""
Questa applicazione riflette l’aspetto di «scatola nera» che questi sistemi di valutazione automatizzati spesso hanno. 
Gli utenti (e le persone valutate) non capiscono necessariamente il processo di attribuzione del punteggio. 
Questo problema è particolarmente evidente con l’algoritmo FOTRES, usato in molti cantoni svizzeri, come mostrano [AlgorithmWatch](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/) e lo studio di Tim Räz [sull’argomento](https://link.springer.com/article/10.1007/s43681-022-00223-y).""")

expander_weight = st.expander("Tutte le variabili hanno lo stesso impatto sul punteggio?")
expander_weight.write("""
Non tutte le informazioni giocano lo stesso ruolo nel calcolo del punteggio di recidiva. 
Per esempio, alcune variabili (come l’«età») pesano di più di altre. 
Ciò deriva dall’architettura dell’algoritmo usato per la valutazione, cioè dalla sua costruzione e programmazione.""")

expander_missing = st.expander("Il sistema sarebbe più giusto se eliminassimo alcune informazioni sensibili (genere, origine, ecc.)?")
expander_missing.write("""
Eliminare alcune informazioni non significa necessariamente meno discriminazione. 
Per esempio, anche se l’origine o l’etnia non sono prese in considerazione nei sistemi svizzeri (come [FaST](https://www.rosnet.ch/fr-ch/Processus/Tri) o [FOTRES](https://www.mwv-berlin.de/produkte/!/title/fotres--forensisches-operationalisiertes-therapie-risiko-evaluations-system/id/804)), la discriminazione può essere presente attraverso i dati e le pratiche. 
Il profilaggio razziale è un buon esempio: influenza le statistiche di arresti o controlli di polizia. 
Si può anche usare il codice postale per dedurre indirettamente l’origine di una persona tramite statistiche demografiche regionali.""")

expander_box = st.expander("Qual è la situazione in Svizzera?")
expander_box.write("""
Non esiste un consenso federale su come valutare il rischio di recidiva in Svizzera. 
I due principali sistemi usati sono FaST e FOTRES, sebbene [i cantoni latini non li usino ancora](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine). 
In [un articolo del 2018](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine), la SRF sottolinea che questi sistemi mancano di valutazioni esterne e validazioni per giudicare la loro qualità. 
I cantoni latini usano un sistema chiamato [PLESORR](https://www.cldjp.ch/plesorr/). Se desidera una visione più generale dei sistemi automatizzati in Svizzera, legga [questo rapporto](https://automatingsociety.algorithmwatch.org/wp-content/uploads/2021/01/Automating-Society-Report-2020-CH-Edition-DE-FR-IT-EN.pdf).""")

st.divider()

st.subheader("Sondaggio")

with st.form(key='app_form'):
    like = st.text_input("Cosa vi è piaciuto di questa esperienza?")
    dislike = st.text_input("Cosa avrebbe potuto essere diverso / migliore?")
    offensive = st.checkbox("Avete trovato l’esperienza con le immagini offensiva (spuntare se SÌ)?")

    submit_button = st.form_submit_button("Invia")

    if submit_button:
        if like or dislike or offensive :
            client = authenticate_google_sheets()
            form_data = [like, dislike, offensive]
            update_google_sheet(form_data)
            st.success("Feedback inviato con successo, grazie!")
        else:
            st.error("Si prega di compilare tutti i campi obbligatori.")
