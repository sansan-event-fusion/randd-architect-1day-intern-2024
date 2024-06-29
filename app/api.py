import logging
import re

import geocoder
import requests

from app import API_URL


def get_user_list(offset: int, limit: int):
    users = requests.get(API_URL + "api/cards/", params={
                         "offset": offset, "limit": limit}, timeout=10).json()

    users_list = [f"{user['full_name']} / {user['user_id']}" for user in users]

    return users_list


def get_user(user_id: str):
    user = requests.get(
        API_URL + f"api/cards/{user_id}", timeout=10).json()[0]

    address = re.sub(r"[0-9-]", "", user["address"])
    ret = geocoder.osm(address, timeout=5.0)
    if ret:
        latlng = ret.latlng
        user["lat"] = latlng[0]
        user["lon"] = latlng[1]
        user["color"] = "#FF0000"
        user["similarity"] = 100

    return user


def get_similar_users(user_id: str):
    similar_users = requests.get(
        API_URL + f"api/cards/{user_id}/similar_top10_users", timeout=10).json()

    return_users = []

    for similar_user in similar_users:
        address = re.sub(r"[0-9-]", "", similar_user["address"])
        try:
            ret = geocoder.osm(address, timeout=5.0)
            if ret:
                latlng = ret.latlng
                similar_user["lat"] = latlng[0]
                similar_user["lon"] = latlng[1]
                similar_user["similarity"] = float(
                    similar_user["similarity"]) * 1000
                similar_user["color"] = "#0000FF"
                return_users.append(similar_user)
        except Exception as e:
            logging.exception(f"Error: {e}")  # noqa: G004, TRY401

    return return_users
