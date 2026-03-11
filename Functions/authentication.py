#Authentication
import streamlit as st
import json
import re
import os
from Functions.mydatabase import get_db


#Session State Management
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "Auth"
if 'ai_output' not in st.session_state: st.session_state.ai_output = ""

def navigate_to(page):
    st.session_state.page = page
    st.rerun()

def auth_page():
    st.title("🚀 Pro Job Portal")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="l_email")
        pwd = st.text_input("Password", type="password", key="l_pwd")
        if st.button("Login"):
            conn = get_db()
            user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, pwd)).fetchone()
            if user:
                st.session_state.user = {"email": user[1], "role": user[4], "id": user[0]}
                if user[4] == "Admin": navigate_to("Admin")
                elif user[5] == 0: navigate_to("Profile Builder")
                else: navigate_to("Dashboard")
            else:
                st.error("Invalid credentials")

    with tab2:
        role = st.radio("I am a...", ["User", "Admin"], horizontal=True)
        new_email = st.text_input("Registration Email")
        new_mob = st.text_input("Mobile Number")
        new_pwd = st.text_input("Choose Password", type="password")
        if st.button("Register Account"):
            try:
                conn = get_db()
                conn.execute("INSERT INTO users (email, mobile, password, role) VALUES (?,?,?,?)", 
                             (new_email, new_mob, new_pwd, role))
                conn.commit()
                st.success("Success! Please Login.")
            except: st.error("Email already registered.")