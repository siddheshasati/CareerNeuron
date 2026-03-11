import streamlit as st
import sqlite3
import json
import os
import google.generativeai as genai
from Functions.mydatabase import get_db, init_db
from Functions.authentication import navigate_to, auth_page
from Functions.profilebuilder import profile_builder, my_account
from Functions.dashboard import dashboard
from Functions.adminpage import admin_page

# Import your new feature files
from Functions.career_advisor import career_advisor_ui
from Functions.job_matcher import job_matcher_ui
from Functions.interview_sim import interview_simulator_ui
from Functions.cover_letter import generate_cover_letter_ui

# Simple AI Engine to handle LLM calls
class AI_Engine:
    def __init__(self, api_key):
        genai.configure(api_key='AIzaSyABsixjZhGj3Gyo6UFrpyPg3GOPg41OCkM')
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def get_response(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    # Initialize AI Engine in session state
    if "ai_engine" not in st.session_state:
        # Use your Gemini API Key here
        st.session_state.ai_engine = AI_Engine(api_key="AIzaSyABsixjZhGj3Gyo6UFrpyPg3GOPg41OCkM")

    if st.session_state.user is None:
        auth_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.user['role']}")
        st.sidebar.write(st.session_state.user['email'])
        
        # --- NAVIGATION LOGIC ---
        if st.session_state.user['role'] == "Admin":
            options = ["Admin"]
        else:
            # Check if we were redirected from the Dashboard's "Run Interview Sim" button
            if st.session_state.get("page") == "Interview Simulator":
                default_index = 4
                # Reset the page state after setting the index
                st.session_state.page = None 
            else:
                default_index = 0

            options = [
                "Dashboard", 
                "My Account", 
                "Profile Builder", 
                "AI Career Advisor", 
                "Interview Simulator", 
                "Cover Letter Gen",
                "Job Matching"
            ]
            
        choice = st.sidebar.radio("Navigation", options, index=default_index)
        
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()

        # --- ROUTING LOGIC ---
        if choice == "Dashboard": 
            dashboard()
        elif choice == "My Account": 
            my_account()
        elif choice == "Profile Builder": 
            profile_builder()
        elif choice == "Admin": 
            admin_page()
            
        # New AI Features Routing
        elif choice == "AI Career Advisor": 
            career_advisor_ui()
        elif choice == "Interview Simulator": 
            interview_simulator_ui()
        elif choice == "Cover Letter Gen": 
            generate_cover_letter_ui()
        elif choice == "Job Matching":
            job_matcher_ui()

if __name__ == "__main__":
    init_db() # Ensure DB is ready
    main()