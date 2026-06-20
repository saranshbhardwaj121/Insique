import streamlit as st


st.set_page_config(page_title="Insique", page_icon="SF", layout="wide")

st.title("Insique")
st.caption("Market intelligence platform foundation")

st.info("Backend foundation is in place. Next step is sprint-by-sprint feature implementation.")

with st.container(border=True):
    st.subheader("MVP Scope")
    st.write(
        "Authentication, watchlists, market data caching, charts, chart intelligence, and trade journaling."
    )
