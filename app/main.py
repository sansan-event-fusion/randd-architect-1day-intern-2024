#!/usr/bin/env python

import streamlit as st

from app.api import get_similar_users, get_user, get_user_list
from app.funcs import plot_users

user = st.selectbox(
    "調べたいユーザをお選びください。",
    tuple(get_user_list(offset=0, limit=2000)),
    index=None
)

if user:
    users_plots = []

    user_id = user.split("/")[-1].strip()
    st.write("You selected:", user)
    similar_users = get_similar_users(user_id)
    users_plots.extend(similar_users)

    target_user = get_user(user_id)

    users_plots.append(target_user)

    plot_users(users_plots)
