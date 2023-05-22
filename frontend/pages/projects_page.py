import streamlit as st
import httpx
from sidebar import authenticated, not_authenticated
from dateutil.parser import parse
from streamlit_extras.switch_page_button import switch_page
import os

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(page_title="my projects", layout="wide")

if "selected_project" not in st.session_state:
    st.session_state.selected_project = 0


def set_specific_project(id) -> None:
    st.session_state.selected_project = id


def remove_task(project_id, task_id) -> None:
    response = httpx.delete(
        url=f"http://{BACKEND_URL}/project/{project_id}/task/{task_id}",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
    )
    if response.status_code != 200:
        st.error(response.text)


def remove_user(project_id, email) -> None:
    response = httpx.delete(
        url=f"http://{BACKEND_URL}/project/{project_id}/delete/user?email_to_delete={email}",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
    )
    if response.status_code != 200:
        st.error(response.text)


def add_user(porject_id, email) -> None:
    response = httpx.put(
        url=f"http://{BACKEND_URL}/project/{porject_id}/add/user?email_to_add={email}",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
    )
    if response.status_code != 200:
        st.error(response.text)


def add_manager(porject_id, email) -> None:
    response = httpx.put(
        url=f"http://{BACKEND_URL}/project/{porject_id}/add/manager?email_to_add={email}",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
    )
    if response.status_code != 200:
        st.error(response.text)


def is_manager(user_id, project) -> bool:
    for manager in project["managers"]:
        if manager["id"] == user_id:
            return True
    return False


def create_project_form() -> None:
    st.session_state.create_button = True
    with st.form("create_project", clear_on_submit=True):
        title_val = st.text_input("title")
        description_val = st.text_input("description")
        submitted = st.form_submit_button("Submit")
        if submitted:
            del st.session_state.create_button
            response = httpx.post(
                url=f"http://{BACKEND_URL}/project/create/",
                json={"title": title_val, "description": description_val},
                headers={"Authorization": f"Bearer {st.session_state.token}"},
            )
            if response.status_code == 200:
                st.success("project created")
                st.experimental_rerun()

            else:
                st.error("error in creating project")


def manager_util_form() -> None:
    col, _ = st.columns((1, 2))
    option = col.selectbox(
        label="manage users", options=("add user", "add manager", "delete user")
    )
    if option:
        with col.form("manager utils", clear_on_submit=True):
            user_email = st.text_input("user email")
            submitted = st.form_submit_button("Submit")
            if submitted:
                if user_email != "":
                    match option:
                        case "add user":
                            add_user(st.session_state.selected_project, user_email)
                        case "add manager":
                            add_manager(st.session_state.selected_project, user_email)
                        case "delete user":
                            remove_user(st.session_state.selected_project, user_email)
                else:
                    st.error("fill the blank")


def display_users(users, managers) -> None:
    users_tab, managers_tab = st.tabs(["all users", "managers"])
    with users_tab:
        for user_id, user_details in users.items():
            col1, col2, col3 = st.columns((1, 2, 1))
            col1.text(user_details["username"])
            col2.text(user_details["email"])
            if st.session_state.is_manager:
                col3.button(
                    "remove user",
                    key=f"user{user_id}",
                    on_click=remove_user,
                    args=(id, user_details["email"]),
                )
    with managers_tab:
        for manager in managers:
            col1, col2 = st.columns((1, 2))
            col1.text(manager["username"])
            col2.text(manager["email"])


def display_task(task, users, curr_tab) -> None:
    cols = curr_tab.columns((1, 2, 1, 1, 1, 1, 1))
    with curr_tab:
        cols[0].write(task["title"])
        cols[1].write(task["description"])
        cols[2].write(parse(task["date_of_creation"]).strftime("%d-%m-%Y %H:%M"))
        cols[3].write(parse(task["deadline"]).strftime("%d-%m-%Y %H:%M"))
        if users[task["created_by_id"]] == None:
            cols[4].write("deleted user")
        else:
            cols[4].write(users[task["created_by_id"]]["username"])
        if task["assignee_id"] == None:
            cols[5].write("not assigned")
        else:
            cols[5].write(users[task["assignee_id"]]["username"])
        task_id = task["id"]
        task_update = cols[6].button("edit task", key=f"task_update_{task_id}")
        if task_update:
            st.session_state.users = users
            st.session_state.task = task
            st.session_state.task_mode = "update"
            switch_page("task_page")
        if st.session_state.is_manager:
            cols[6].button(
                "delete task",
                key=f"task_delete_{task_id}",
                on_click=remove_task,
                args=(id, task_id),
            )


def display_projects(projects):
    cols = st.columns((1, 2, 1))
    fields = ["title", "description", "action"]
    for col, field in zip(cols, fields):
        col.subheader(field)
    for project in projects:
        col1, col2, col3 = st.columns((1, 2, 1))
        col1.write(project["title"])
        col2.write(project["description"])
        col3.button(
            "enter project page",
            key=project["id"],
            on_click=set_specific_project,
            args=(project["id"],),
        )


if "token" not in st.session_state:
    not_authenticated()
    st.warning("this page for logged in users only")

elif st.session_state.selected_project == 0:
    authenticated()
    st.title("My Projects")
    pressed = st.button("create project")
    if "create_button" not in st.session_state:
        st.session_state.create_button = False
    if pressed or st.session_state.create_button:
        create_project_form()

    response = httpx.get(
        url=f"http://{BACKEND_URL}/project/my-projects/",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
    )
    if response.status_code == 200:
        display_projects(response.json())
    else:
        st.error(response.text)

else:
    authenticated()
    if st.button("go back to all project's page"):
        del st.session_state.selected_project
        st.experimental_rerun()

    id = st.session_state.selected_project

    project_details = httpx.get(
        url=f"http://{BACKEND_URL}/project/{id}/",
        headers={"Authorization": f"Bearer {st.session_state.token}"},
    )
    if project_details.status_code == 200:
        project_details = project_details.json()
        st.session_state.is_manager = is_manager(st.session_state.id, project_details)
        users = {
            user["id"]: {"email": user["email"], "username": user["username"]}
            for user in project_details["users"]
        }
        st.title(project_details["title"])
        st.subheader(project_details["description"])

        if st.session_state.is_manager:
            manager_util_form()

        display_users(users, project_details["managers"])

        st.header("Tasks")

        if st.session_state.is_manager:
            if st.button("create task"):
                st.session_state.users = users
                st.session_state.task_mode = "create"
                switch_page("task_page")

        tasks = httpx.get(
            url=f"http://{BACKEND_URL}/project/{id}/task/",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
        )
        if tasks.status_code == 200:
            tasks = tasks.json()
            tabs = st.tabs(["in progress", "completed"])
            for tab in tabs:
                cols = tab.columns((1, 2, 1, 1, 1, 1, 1))
                fields = ["title:", "description:", "date of creation:","deadline:","created by:","assigned to:",""]
                for col, field in zip(cols, fields):
                    col.write(field)
            for task in tasks:
                if task["status"] == "IN_PROGRESS":
                    curr_tab = tabs[0]
                else:
                    curr_tab = tabs[1]
                display_task(task, users, curr_tab)
        else:
            st.error(tasks.text)
