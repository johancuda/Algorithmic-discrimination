import streamlit as st

st.logo("assets/img/BFH_Logo_C_en_100_RGB.png", size="large")


with st.sidebar:
    # st.image("assets/img/qr_code.png", caption="Scan this to test this experience at home or on your device")
    language = st.selectbox("Select a language", ("English", "French", "German", "Italian"))

main_page = f"app_{language}.py"
about_page = f"about_{language}.py"
resources_page = f"resources_{language}.py"

lang_dict = {
    "English": {
        "home" : "Homepage",
        "resources" : "Resources",
        "about" : "About"
    },
    "French": {
        "home" : "Page d'accueil",
        "resources" : "Ressources",
        "about" : "À propos"
    },
    "German": {
        "home" : "Homepage",
        "resources" : "Ressourcen",
        "about" : "Über"
    },
    "Italian": {
        "home" : "Pagina iniziale",
        "resources" : "Risorse",
        "about" : "Info"
    }
}

pg = st.navigation([st.Page(main_page, title=lang_dict[language]['home'], default=True, icon="🏠"),
                    # st.Page("app_pics.py", title="Second experience"),
                    st.Page(resources_page, title=lang_dict[language]['resources'], icon="📖"),
                    st.Page(about_page, title=lang_dict[language]['about'], icon="ℹ️")])
pg.run()