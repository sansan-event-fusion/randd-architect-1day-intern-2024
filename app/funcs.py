import pandas as pd
import streamlit as st


def plot_users(similar_users):
    data_frame = pd.DataFrame(similar_users)

    if not data_frame.empty:
        st.map(
            data_frame,
            latitude="lat",
            longitude="lon",
            size="similarity",
            color="color",
        )
