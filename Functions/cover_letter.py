import streamlit as st
from Functions.mydatabase import get_db

def generate_cover_letter_ui():
    st.title("✉️ Profile-Linked Cover Letter")
    
    target_role = st.text_input("Target Job Role")
    
    if st.button("Generate Letter from My Profile"):
        # Fetching all profile data from database
        conn = get_db()
        u = conn.execute("SELECT full_name, city, state, education, experience FROM users WHERE email=?", 
                        (st.session_state.user['email'],)).fetchone()
        conn.close()

        if u:
            prompt = f"""
            Write a professional cover letter for the role of {target_role}.
            User Details:
            Name: {u['full_name']}
            Location: {u['city']}, {u['state']}
            Education: {u['education']}
            Experience: {u['experience']}
            
            Make it persuasive and mention how their education aligns with {target_role}.
            """
            
            with st.spinner("Drafting..."):
                letter = st.session_state.ai_engine.get_response(prompt)
                st.text_area("Your Generated Letter", letter, height=450)
        else:
            st.error("Please complete your profile first!")