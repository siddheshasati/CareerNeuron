import streamlit as st

def interview_simulator_ui():
    st.title("🎙️ AI Interview Simulator")
    
    # 1. Input Section
    col1, col2 = st.columns(2)
    with col1:
        target_company = st.text_input("Target Company", placeholder="e.g., Google, TCS, Infosys")
        target_role = st.text_input("Target Role", placeholder="e.g., Python Developer")
    with col2:
        experience = st.selectbox("Experience Level", ["Fresher", "1-3 Years", "5+ Years"])
        expected_ctc = st.text_input("Expected CTC")

    # Initialize session state for questions and answers
    if "interview_questions" not in st.session_state:
        st.session_state.interview_questions = None
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    # Step 1: Generate Questions
    if st.button("Generate Mock Interview Questions"):
        prompt = f"""
        Act as an interviewer for {target_company}. Role: {target_role}. Experience: {experience}.
        Tasks:
        1. Search for real interview history for {target_company}.
        2. Provide exactly 5 technical questions frequently asked and 1 or 2 coding questions related to {target_role}. 
        Format: Return ONLY the questions separated by a pipe symbol '|' so I can parse them.
        Example: Question 1 | Question 2 | Question 3 | Question 4 | Question 5
        """
        
        with st.spinner("Analyzing company interview patterns..."):
            raw_questions = st.session_state.ai_engine.get_response(prompt)
            # Splitting the AI response into a list
            st.session_state.interview_questions = [q.strip() for q in raw_questions.split("|")]
            st.session_state.user_answers = {i: "" for i in range(len(st.session_state.interview_questions))}
            st.rerun()

    # Step 2: Display Questions and Answer Bars
    if st.session_state.interview_questions:
        st.write("---")
        st.subheader("📝 Your Interview Panel")
        
        for i, q in enumerate(st.session_state.interview_questions):
            st.info(f"**Q{i+1}:** {q}")
            st.session_state.user_answers[i] = st.text_area(f"Your Answer to Q{i+1}", 
                                                            key=f"ans_{i}", 
                                                            placeholder="Type your detailed answer here...")

        # Step 3: Evaluate at the Last
        if st.button("Submit All Answers for AI Evaluation"):
            with st.spinner("Evaluating your performance..."):
                # Constructing the evaluation prompt
                eval_data = ""
                for i, q in enumerate(st.session_state.interview_questions):
                    ans = st.session_state.user_answers[i]
                    eval_data += f"Question: {q}\nUser Answer: {ans}\n\n"

                eval_prompt = f"""
                Analyze the following interview answers for a {target_role} position at {target_company}.
                Data:
                {eval_data}
                
                For each answer:
                1. State if it is Correct/Incorrect/Partially Correct.
                2. Give an Accuracy Percentage (0-100%).
                3. Suggest specific improvements or missing technical keywords.
                
                Finally, give an overall 'Hiring Probability' score.
                """
                
                evaluation = st.session_state.ai_engine.get_response(eval_prompt)
                st.write("---")
                st.header("📊 AI Performance Report")
                st.markdown(evaluation)
                
                if st.button("Start New Interview"):
                    st.session_state.interview_questions = None
                    st.rerun()