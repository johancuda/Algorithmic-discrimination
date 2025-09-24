import streamlit as st

def about():
    st.title("Resources")

    container = st.container(border=True)
    container.write(
        "You can find here various resources about risk assessment systems."
    )

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

    

pg = st.navigation([st.Page("app.py", title="Home", default=True), st.Page(about, title="Resources")])
pg.run()