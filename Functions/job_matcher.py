import streamlit as st
import json
import sqlite3
from Functions.job_api_handler import JobAPIHandler
from Functions.mydatabase import get_db

def job_matcher_ui():
    # Force a UI refresh to clear the "No docs" bug
    st.empty() 
    st.title("🎯 AI Job Matcher")
    st.write("Find jobs that perfectly match your profile skills.")

    # 1. Fetch and Parse User Skills (Index 8 for Education)
    conn = get_db()
    user_data = conn.execute("SELECT education, experience FROM users WHERE email=?", 
                            (st.session_state.user['email'],)).fetchone()
    conn.close()

    all_skills = []
    if user_data:
        try:
            edu = json.loads(user_data['education']) if user_data['education'] else []
            for item in edu:
                if len(item) > 8 and item[8]: all_skills.append(item[8])
            
            exp = json.loads(user_data['experience']) if user_data['experience'] else []
            for item in exp:
                if len(item) > 2 and item[2]: all_skills.append(item[2])
        except Exception as e:
            st.error(f"Data Parsing Error: {e}")

    skill_context = ", ".join(set(all_skills))

    # 2. Search Logic
    api_handler = JobAPIHandler()
    query = st.text_input("Enter Job Role to Match (e.g., Python Developer)", key="matcher_search_input")
    
    if st.button("Find Matches", key="matcher_search_btn"):
        if not query:
            st.warning("Please enter a role.")
            return

        with st.spinner("Searching and Scoring..."):
            # Fetch Jobs
            jobs = []
            try:
                jobs.extend(api_handler.fetch_adzuna(query))
                jobs.extend(api_handler.fetch_jooble(query))
            except: pass

            if not jobs:
                st.info("No matching jobs found.")
            else:
                for i, job in enumerate(jobs[:10]): # Limit to top 10 for speed
                    with st.container():
                        c1, c2 = st.columns([3, 1])
                        title = job.get('title', 'N/A')
                        
                        with c1:
                            st.subheader(title)
                            st.write(f"🏢 {job.get('company', 'Unknown')}")
                            
                            # AI Score Calculation
                            prompt = f"User Skills: {skill_context}. Job: {title}. Give match % and 1 reason."
                            score = st.session_state.ai_engine.get_response(prompt)
                            st.success(f"**AI Fit Score:** {score}")

                        with c2:
                            st.write("##")
                            st.link_button("Apply", job.get('link', '#'), use_container_width=True)

                        st.divider()
