import streamlit as st

el = range(10)

if "test" not in st.session_state:
    st.session_state["test"] = [1,2]
st.write(st.session_state["test"])
st.multiselect(
    "A",
    options=el,
    default=st.session_state["test"],
    key='test'
)
st.write(st.session_state["test"])