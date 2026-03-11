import streamlit as st
from Functions.mydatabase import get_db
import PyPDF2
import os
import sqlite3
import json

def extract_resume_text(file_path):
    """Helper to extract text from the path stored in resume_path column."""
    if not file_path or not os.path.exists(file_path):
        return "No resume file found."
    
    try:
        with open(file_path, "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        return f"Error reading resume: {str(e)}"

def career_advisor_ui():
    st.title("🤖 AI Career Path Advisor")

    # 1. Fetch data
    conn = get_db()
    conn.row_factory = sqlite3.Row 
    user_row = conn.execute(
        "SELECT education, experience, resume_path FROM users WHERE email=?", 
        (st.session_state.user['email'],)
    ).fetchone()
    conn.close()

    if not user_row:
        st.error("User profile not found.")
        return

    # --- NEW: PARSE SKILLS FROM JSON ---
    all_skills = []
    
    # Parse Education Skills (at index 8 based on your save logic)
    try:
        edu_list = json.loads(user_row['education']) if user_row['education'] else []
        for edu in edu_list:
            if len(edu) > 8 and edu[8]:
                all_skills.append(edu[8])
    except: pass

    # Parse Experience Roles/Skills (at index 2)
    try:
        exp_list = json.loads(user_row['experience']) if user_row['experience'] else []
        for exp in exp_list:
            if len(exp) > 2 and exp[2]:
                all_skills.append(exp[2])
    except: pass

    skill_context = ", ".join(set(all_skills)) # Use set to remove duplicates
    # -----------------------------------

    resume_content = extract_resume_text(user_row['resume_path'])

    if "career_chat_history" not in st.session_state:
        st.session_state.career_chat_history = []

    # Display Chat
    for message in st.session_state.career_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about tech stacks, career shifts, or job trends..."):
        st.session_state.career_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build context-aware prompt with SKILLS
        full_prompt = f"""
        CONTEXT:
        - User Skills: {skill_context}
        - User Education: {user_row['education']}
        - User Experience: {user_row['experience']}
        - Resume Content: {resume_content[:1500]}

        USER QUESTION: {prompt}

        INSTRUCTIONS:
        You are an expert Career Mentor.
        1. Look specifically at the 'User Skills' provided above.
        2. Suggest the best technology or role the user should pursue based on these skills.
        3. You are a Career Mentor. Analyze the user's background and resume, and provide personalized career advice.
        4.  Suggest specific technologies or career paths they should pursue.
        5. If the user's skills are outdated, suggest which modern tech stack they should switch to.
        6. Help user to learn about the latest job market trends and which skills are in demand and which are declining.
        7. Help user to learn any subject or topic related to career growth and development.
        8. Ask User about their projects if they have made anything and give feedback on it that how to improve and if user not 
        made the projects then suggest them to make projects and give them the project ideas based on their skills and experience.
        9. Only answer career-related queries
        """
        
        with st.spinner("Consulting AI Career Expert..."):
            response = st.session_state.ai_engine.get_response(full_prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.career_chat_history.append({"role": "assistant", "content": response})