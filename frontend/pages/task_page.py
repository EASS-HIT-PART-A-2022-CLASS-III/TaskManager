import httpx
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from dateutil.parser import parse
from datetime import datetime
from sidebar import authenticated
import time
import os

BACKEND_URL = os.getenv("BACKEND_URL")


def task_update():
    users = st.session_state.users
    task = st.session_state.task

    task_title = st.text_input("Task Title", value=task["title"])
    task_description = st.text_area("Task Description", value=task["description"])
    task_deadline_date = st.date_input(
        "Task Deadline Date", value=parse(task["deadline"]).date()
    )
    task_deadline_time = st.time_input(
        "Task Deadline Time", value=parse(task["deadline"]).time()
    )
    default_index = (
        list(users).index(task["assignee_id"]) if task["assignee_id"] in users else 0
    )
    task_assignee = st.selectbox(
        "assigne to",
        options=users.keys(),
        index=default_index,
        format_func=lambda x: users[x]["username"],
    )
    options = {"IN_PROGRESS": "in progress", "COMPLETED": "completed"}
    task_status = st.selectbox(
        "status",
        options.keys(),
        index=list(options).index(task["status"]),
        format_func=lambda x: options[x],
    )
    submitted = st.button("Update Task")
    if submitted:
        project_id = task["project_id"]
        task_id = task["id"]
        deadline = datetime.combine(task_deadline_date, task_deadline_time)
        response = httpx.put(
            url=f"http://{BACKEND_URL}/project/{project_id}/task/{task_id}",
            json={
                "title": task_title,
                "description": task_description,
                "status": task_status,
                "deadline": deadline.isoformat(),
                "assignee_id": task_assignee,
            },
            headers={"Authorization": f"Bearer {st.session_state.token}"},
        )
        if response.status_code == 200:
            st.success("updated")
            time.sleep(0.5)
            del st.session_state.users
            del st.session_state.task
            del st.session_state.task_mode
            st.experimental_rerun()
        else:
            st.error(response.json()["detail"])


def task_create():
    task_title = st.text_input("Task Title")
    task_description = st.text_area("Task Description")
    task_deadline_date = st.date_input("Task Deadline Date")
    task_deadline_time = st.time_input("Task Deadline Time")
    options = {"IN_PROGRESS": "in progress", "COMPLETED": "completed"}
    task_status = st.selectbox(
        "status", options.keys(), format_func=lambda x: options[x]
    )
    submitted = st.button("Create Task")
    if submitted:
        if task_title != "" or task_description != "":
            deadline = datetime.combine(task_deadline_date, task_deadline_time)
            response = httpx.post(
                url=f"http://{BACKEND_URL}/project/{st.session_state.selected_project}/task/",
                json={
                    "title": task_title,
                    "description": task_description,
                    "status": task_status,
                    "deadline": deadline.isoformat(),
                },
                headers={"Authorization": f"Bearer {st.session_state.token}"},
            )
            if response.status_code == 200:
                st.success("task created")
                time.sleep(0.5)
                del st.session_state.task_mode
                st.experimental_rerun()
            else:
                st.error(response.json()["detail"])
        else:
            st.error("fill the blank")


if "task_mode" not in st.session_state:
    switch_page("projects_page")
if "token" not in st.session_state:
    switch_page("main")
else:
    authenticated()

    match st.session_state.task_mode:
        case "update":
            task_update()
        case "create":
            task_create()
