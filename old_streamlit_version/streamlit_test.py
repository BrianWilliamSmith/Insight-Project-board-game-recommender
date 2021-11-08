import streamlit as st
import time

st.title("favorite pet")

def print_favorite():
    return "I love my " + favorite_pet

st.write(print_favorite())

favorite_pet = st.selectbox(
    "select a favorite pet",
    ("cat", "dog", "fish"))

