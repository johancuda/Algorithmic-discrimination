import streamlit as st

def resources():
    st.title("Resources")

    st.subheader("About automatic systems in Switzerland")

    """
    - [Automating Society Report 2020](https://automatingsociety.algorithmwatch.org/wp-content/uploads/2021/01/Automating-Society-Report-2020-CH-Edition-DE-FR-IT-EN.pdf)
    - [Die grosse Screening-Maschine](https://www.srf.ch/news/schweiz/rueckfallrisiko-bei-straftaetern-die-grosse-screening-maschine)
    - [Automatisierte Strafjustiz auf wissenschaftlich wackeligen Beinen](https://algorithmwatch.ch/de/fotres-automatisierte-strafjustiz/)
    """

    st.subheader("About FOTRES")

    """
    - [Understanding risk with FOTRES?](https://link.springer.com/article/10.1007/s43681-022-00223-y)
    - [FOTRES - Système d'évaluation des risques thérapeutiques opérationnalisés médico-légaux](https://www.mwv-berlin.de/produkte/!/title/fotres--forensisches-operationalisiertes-therapie-risiko-evaluations-system/id/804)
    - [Risk Assessment Instruments in Repeat Offending: The Usefulness of FOTRES](https://journals.sagepub.com/doi/epdf/10.1177/0306624X09360662)
    - [Algorithm Watch](https://algorithmwatch.ch/de/fotres-simple-mathematik-komplizierte-folgen/)
    """

    st.subheader("About COMPAS")

    """
    - [Machine Bias](https://www.propublica.org/article/machine-bias-risk-assessments-in-criminal-sentencing)
    - [How We Analyzed the COMPAS Recidivism Algorithm](https://www.propublica.org/article/how-we-analyzed-the-compas-recidivism-algorithm)
    - [Compas Analysis on GitHub](https://github.com/propublica/compas-analysis/blob/master/Compas%20Analysis.ipynb)
    """

    st.subheader("About FaST")

    """
    - [ROS, Fall-Screening-Tool FaST](https://algorithmwatch.ch/en/atlas-db/ros-fall-screening-tool-fast/?text=FaST)
    - [Manual – Fall-Screening-Tool](https://www.srf.ch/static/srf-data/data/2018/ros/fast_manual_und_gewichte.pdf)
    """

st.logo("BFH_Logo_C_en_100_RGB.png", size="large")

pg = st.navigation([st.Page("app_user.py", title="Home", default=True), st.Page("app_pics.py", title="Second experience"), st.Page(resources, title="Resources"), st.Page("about.py", title="About")])
pg.run()