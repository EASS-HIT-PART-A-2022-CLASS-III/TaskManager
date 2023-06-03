import streamlit as st
import httpx
from streamlit_extras.switch_page_button import switch_page
from st_pages import hide_pages
import os

BACKEND_URL = os.getenv("BACKEND_URL")


def _login(password_val, email_val) -> None:
    response = httpx.post(
        url=f"http://{BACKEND_URL}/user/login/",
        data={"username": email_val, "password": password_val},
    )
    if response.status_code == 200:
        st.session_state["token"] = response.json()["access_token"]
        st.experimental_rerun()
    else:
        st.error(response.json()["detail"])


def _login_form() -> None:
    st.session_state.pressed_login_button = True
    with st.sidebar.form("login", clear_on_submit=True):
        st.subheader("Login")
        email_val = st.text_input("email")
        password_val = st.text_input("password", type="password")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if password_val != "" and email_val != "":
                _login(password_val, email_val)
                del st.session_state.pressed_login_button
            else:
                st.sidebar.error("fill the blank")


def _register_form() -> None:
    st.session_state.pressed_register_button = True
    with st.sidebar.form("register", clear_on_submit=True):
        st.subheader("Register")
        email_val = st.text_input("email")
        username_val = st.text_input("username")
        password_val = st.text_input("password", type="password")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if password_val != "" and email_val != "" and username_val != "":
                response = httpx.post(
                    url=f"http://{BACKEND_URL}/user/create/",
                    json={
                        "email": email_val,
                        "username": username_val,
                        "password": password_val,
                    },
                )
                if response.status_code == 200:
                    _login(password_val, email_val)
                    del st.session_state.pressed_register_button
                else:
                    st.warning(response.json()["detail"])
            else:
                st.sidebar.error("fill the blank")


def _logout() -> None:
    for key in st.session_state.keys():
        del st.session_state[key]
    switch_page("main")


def not_authenticated() -> None:
    hide_pages(["task_page", "projects_page"])
    col1, col2 = st.sidebar.columns(2)
    if "pressed_login_button" not in st.session_state:
        st.session_state.pressed_login_button = False
    if "pressed_register_button" not in st.session_state:
        st.session_state.pressed_register_button = False

    login_pressed = col1.button(label="Login")
    if login_pressed or st.session_state.pressed_login_button:
        _login_form()
    register_pressed = col2.button(label="Register")
    if register_pressed or st.session_state.pressed_register_button:
        _register_form()


def authenticated() -> None:
    hide_pages(["task_page"])
    logout_pressed = st.sidebar.button(label="LogOut")
    if logout_pressed:
        _logout()
    response = httpx.get(
        url=f"http://{BACKEND_URL}/user/me/",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
    )
    if response.status_code == 200:
        st.session_state.username = response.json()["username"]
        st.session_state.email = response.json()["email"]
        st.session_state.id = response.json()["id"]
        st.sidebar.write(f"Logged in as: {st.session_state.username}")
    else:
        _logout()
