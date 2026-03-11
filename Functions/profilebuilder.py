import streamlit as st
import re
import os
import json
import base64
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from PIL import Image
import PyPDF2
from fpdf import FPDF
from Functions.mydatabase import get_db
from Functions.authentication import navigate_to


# --- 1. Configuration & API ---
st.set_page_config(page_title="CareerNeuron", layout="wide")
# Replace with your actual key or use st.secrets["GEMINI_KEY"]
genai.configure(api_key="GEMINI_API_KEY")




#Helper Function
def init_session_states():
    """Initializes counters for dynamic rows."""
    if 'edu_rows' not in st.session_state: st.session_state.edu_rows = 1
    if 'exp_rows' not in st.session_state: st.session_state.exp_rows = 1

#ATS Checker
def run_ats_checker(text):
    text_lower = text.lower()
    score = 0
    feedback = []

    # 1. Length Check
    words = len(text_lower.split())
    if 300 <= words <= 1000: score += 20
    else: feedback.append("❌ Length: Keep resume between 300-1000 words.")

    # 2. Section Check
    required = ['experience', 'education', 'skills']
    missing = [sec for sec in required if sec not in text_lower]
    if not missing: score += 30
    else:
        score += (30 - (len(missing) * 10))
        for ms in missing: feedback.append(f"❌ Missing Section: Include an '{ms.title()}' header.")

    # 3. Metrics Check
    if re.search(r'\d+%|\d+\s*percent|\$\d+|\d+\+', text_lower): score += 25
    else: feedback.append("❌ Metrics: Add quantifiable numbers.")

    # 4. Action Verbs
    verbs = ['managed', 'developed', 'created', 'led', 'designed', 'implemented']
    found_verbs = [v for v in verbs if v in text_lower]
    if len(found_verbs) >= 3: score += 25
    else:
        score += (len(found_verbs) * 8)
        feedback.append("❌ Action Verbs: Start bullet points with strong verbs.")

    status = "✅ Highly optimized" if score >= 90 else "⚠️ Needs work"
    feedback.insert(0, f"{status} for ATS filters.")
    
    return score, feedback

#Resume Feature
def show_resume_feature():
    st.subheader("📝 Resume & ATS Check")
    
    # 1. Upload & Analyze
    resume_file = st.file_uploader("Upload Resume (PDF only)", type=['pdf'])
    
    if resume_file:
        # Extract text once
        raw_text = extract_text_from_pdf(resume_file)
        score, feedback = run_ats_checker(raw_text)
        
        # Display Score and Progress
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("ATS Score", f"{score}%")
        with col2:
            st.write("") # Padding
            st.progress(score / 100)

        # Action Buttons
        btn_col1, btn_col2 = st.columns(2)
        
        # 2. ✨ AI Auto-Rewrite
        if btn_col1.button("✨ Auto-Rewrite with AI"):
            with st.spinner("AI is generating optimized bullet points..."):
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"""
                    Act as an expert ATS resume writer. Review this text:
                    1. Rewrite the 3 most important work experience points with metrics.
                    2. Rewrite project descriptions concisely.
                    3. List specific changes to reach >90% score.
                    Do not use emojis in the result.
                    Text: {raw_text}
                    """
                    response = model.generate_content(prompt)
                    st.session_state.ai_output = response.text
                except Exception as e:
                    st.error(f"AI Error: {e}")

        # Feedback Box (Standard ATS Feedback or AI Output)
        display_text = "\n\n".join(feedback)
        if 'ai_output' in st.session_state:
            display_text = f"✨ AI OPTIMIZED BULLET POINTS ✨\n\n{st.session_state.ai_output}"
        
        st.text_area("Analysis & Suggestions", value=display_text, height=250)

        # 3. 💾 Export to PDF
        if 'ai_output' in st.session_state:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            # Clean text for FPDF (Latin-1 compatibility)
            clean_pdf_text = st.session_state.ai_output.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, txt=clean_pdf_text)
            
            # Use Download Button instead of filedialog
            st.download_button(
                label="💾 Download Optimized PDF",
                data=pdf.output(dest='S').encode('latin-1'),
                file_name="Optimized_Resume.pdf",
                mime="application/pdf"
            )

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() for page in reader.pages])

def generate_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

def show_pdf_preview(text):
    """Encodes PDF bytes to Base64 to display in a web iframe."""
    try:
        pdf_bytes = generate_pdf_bytes(text)
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        # Create the HTML iframe string
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        
        # FIX: The argument name must be exactly 'unsafe_allow_html'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Preview Error: {e}")

# Profile Builder

def profile_builder():
    st.title("🛠️ Build Your Professional Profile")
    init_session_states()

    # --- 1. Personal Details Section ---
    with st.expander("1. Personal Details", expanded=True):
        col1, col2, col3 = st.columns([1, 2, 2])
        
        # Profile Picture logic
        with col1:
            st.write("Profile Pic")
            pic = st.file_uploader("Upload", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
            if pic: st.image(pic, width=100)

        with col2:
            full_name = st.text_input("Full Name", placeholder="Siddhesh ...")
            dob = st.text_input("DOB (MM/DD/YYYY)", placeholder="01/01/2000")
            gender = st.selectbox("Gender", ["Male", "Female", "Trans", "Prefer not to say"])

        with col3:
            city = st.text_input("City", key="city_input")
            # Mimicking your auto-fill pincode logic
            pincode = st.text_input("Pincode (Auto-generated)", value="411001" if city else "", disabled=True)
            state = st.text_input("State")
            country = st.text_input("Country", value="India")

        address = st.text_area("Full Address", placeholder="Enter full address here...")
        mobile_col1, mobile_col2 = st.columns([1, 3])
        country_code = mobile_col1.selectbox("Code", ["+91", "+1", "+44", "+61"])
        mobile_no = mobile_col2.text_input("Mobile Number")

    # --- 2. Education Section (Dynamic Rows) ---
    with st.expander("2. Education", expanded=False):
        edu_data = []
        for i in range(st.session_state.edu_rows):
            st.markdown(f"**Entry #{i+1}**")
            r1c1, r1c2, r1c3, r1c4 = st.columns([2, 1, 2, 1])
            inst = r1c1.text_input("Institution Name", key=f"inst_{i}")
            e_city = r1c2.text_input("City", key=f"ecity_{i}")
            degree = r1c3.text_input("Degree", key=f"deg_{i}")
            e_type = r1c4.selectbox("Type", ["Full Time", "Part Time"], key=f"etype_{i}")
            
            r2c1, r2c2, r2c3, r2c4, r2c5 = st.columns(5)
            stream = r2c1.text_input("Stream", key=f"stream_{i}")
            start = r2c2.text_input("Start (MM/YYYY)", key=f"estart_{i}")
            end = r2c3.text_input("End (MM/YYYY)", key=f"eend_{i}")
            grade = r2c4.text_input("SGPA/%", key=f"grade_{i}")
            skills = r2c5.text_input("Skills", key=f"eskills_{i}")
            edu_data.append([inst, e_city, degree, e_type, stream, start, end, grade, skills])
            st.divider()
        
        if st.button("➕ Add Educational Detail"):
            st.session_state.edu_rows += 1
            st.rerun()

    # --- 3. Experience Section (Dynamic Rows) ---
    with st.expander("3. Experience", expanded=False):
        exp_data = []
        for j in range(st.session_state.exp_rows):
            st.markdown(f"**Job #{j+1}**")
            x1, x2, x3, x4, x5 = st.columns(5)
            comp = x1.text_input("Company Name", key=f"comp_{j}")
            loc = x2.text_input("Location", key=f"loc_{j}")
            role = x3.text_input("Job Role", key=f"role_{j}")
            j_type = x4.selectbox("Type", ["Permanent", "Internship"], key=f"jtype_{j}")
            ctc = x5.text_input("CTC / Stipend", key=f"ctc_{j}")
            
            x_row2_1, x_row2_2, x_row2_3 = st.columns([1, 1, 2])
            x_start = x_row2_1.text_input("Start (MM/YYYY)", key=f"xstart_{j}")
            is_current = x_row2_3.checkbox("Currently working here", key=f"curr_{j}")
            x_end = x_row2_2.text_input("End (MM/YYYY)", key=f"xend_{j}", disabled=is_current, value="Present" if is_current else "")
            exp_data.append([comp, loc, role, j_type, ctc, x_start, x_end])
            st.divider()

        if st.button("➕ Add Job Experience"):
            st.session_state.exp_rows += 1
            st.rerun()

    # --- 4. Resume Section (Same as previous fix) ---

    with st.expander("3. Resume ATS & AI Optimizer"):
        file = st.file_uploader("Upload PDF Resume", type=['pdf'], key="profile_resume_uploader")
        
        if file:
            # Step 1: Extract and Check ATS Score
            raw_text = extract_text_from_pdf(file)
            score, feedback = run_ats_checker(raw_text)
            
            st.info(f"Resume Detected: {len(raw_text.split())} words.")
            
            col_m1, col_m2 = st.columns([1, 2])
            col_m1.metric("ATS Score", f"{score}%")
            col_m2.write("###") # Vertical alignment
            col_m2.progress(score / 100)
            
            # Step 2: AI Optimization
            if st.button("✨ Optimize Projects with AI"):
                with st.spinner("AI is analyzing technical depth..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash')
                        prompt = f"""
                        Act as an expert ATS resume writer. Review this text:
                        1. Rewrite the 3 most important work experience points with metrics.
                        2. Rewrite project descriptions concisely.
                        3. List specific changes to reach >90% score.
                        Do not use emojis in the result.
                        Text: {raw_text}
                        """
                        response = model.generate_content(prompt)
                        st.session_state.ai_output = response.text
                    except Exception as e:
                        st.error(f"AI Error: {e}")

            # Step 3: Show Feedback or AI Suggestions
            if st.session_state.ai_output:
                st.subheader("Live Preview & Suggestions")
                st.text_area("AI Suggestions (Copy-Pasteable)", value=st.session_state.ai_output, height=200)
                
                # Show PDF Preview (Custom Function)
                show_pdf_preview(st.session_state.ai_output)
                
                # Download Button
                st.download_button(
                    label="💾 Download Optimized PDF",
                    data=generate_pdf_bytes(st.session_state.ai_output), 
                    file_name="Optimized_Resume.pdf",
                    mime="application/pdf"
                )
            else:
                # Show standard ATS feedback if AI hasn't run yet
                st.text_area("ATS Analysis", value="\n\n".join(feedback), height=200)

    
    # --- Final Save Logic ---
    
    if st.button("🚀 Save Profile & Launch Dashboard", type="primary", use_container_width=True):
        
        # 1. PERMANENT FIX: Pull Education directly from Session State Keys
        final_edu_list = []
        for i in range(st.session_state.get('edu_rows', 1)):
            # We fetch using the exact unique keys assigned in the UI
            inst = st.session_state.get(f"inst_{i}", "").strip()
            if inst:  # Only save if the name isn't empty
                final_edu_list.append([
                    inst,
                    st.session_state.get(f"ecity_{i}", ""),
                    st.session_state.get(f"deg_{i}", ""),
                    st.session_state.get(f"etype_{i}", ""),
                    st.session_state.get(f"stream_{i}", ""),
                    st.session_state.get(f"estart_{i}", ""),
                    st.session_state.get(f"eend_{i}", ""),
                    st.session_state.get(f"grade_{i}", ""),
                    st.session_state.get(f"eskills_{i}", "")
                ])

        # 2. PERMANENT FIX: Pull Experience directly from Session State Keys
        final_exp_list = []
        for j in range(st.session_state.get('exp_rows', 1)):
            comp = st.session_state.get(f"comp_{j}", "").strip()
            if comp:
                final_exp_list.append([
                    comp,                                    # [0] Company
                    st.session_state.get(f"loc_{j}", ""),    # [1] Location
                    st.session_state.get(f"role_{j}", ""),   # [2] Role
                    st.session_state.get(f"jtype_{j}", ""),  # [3] Type
                    st.session_state.get(f"ctc_{j}", ""),    # [4] CTC
                    st.session_state.get(f"xstart_{j}", ""), # [5] Start
                    st.session_state.get(f"xend_{j}", "")    # [6] End
                ])

        # 3. Handle Image
        img_base64 = ""
        if pic is not None:
            img_base64 = base64.b64encode(pic.getvalue()).decode()

        # 4. Final Database Commit
        # 4. Final Database Commit
        try:
            # --- NEW: HANDLE RESUME SAVING ---
            resume_path_to_save = None
            if file is not None:
                # Create a directory for resumes if it doesn't exist
                if not os.path.exists("uploads/resumes"):
                    os.makedirs("uploads/resumes")
                
                # Create a unique filename using user's email
                safe_email = st.session_state.user['email'].replace("@", "_").replace(".", "_")
                resume_path_to_save = f"uploads/resumes/{safe_email}_resume.pdf"
                
                with open(resume_path_to_save, "wb") as f:
                    f.write(file.getbuffer())
            # ---------------------------------

            conn = get_db()
            # Added resume_path=? to the query
            conn.execute('''UPDATE users SET profile_completed=1, full_name=?, dob=?, gender=?, 
                            address=?, city=?, state=?, country=?, mobile=?, 
                            education=?, experience=?, ai_suggestions=?, profile_pic=?, pincode=?,
                            resume_path=? WHERE email=?''',
                         (full_name or "", dob or "", gender or "", address or "", city or "", 
                          state or "", country or "", f"{country_code} {mobile_no}", 
                          json.dumps(final_edu_list), json.dumps(final_exp_list), 
                          st.session_state.get('ai_output', ""), img_base64, pincode or "", 
                          resume_path_to_save, # The path to the saved file
                          st.session_state.user['email']))
            conn.commit()
            
            st.success("✅ Profile and Resume permanently saved!")
            navigate_to("Dashboard")
        except Exception as e:
            st.error(f"Save Failure: {e}")
            
# My Account (View & Edit) ---
def my_account():
    st.title("👤 Professional Profile")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (st.session_state.user['email'],)).fetchone()
    
    # Organize data into tabs for clarity
    tab_overview, tab_edu, tab_exp, tab_edit = st.tabs([
        "📄 Overview", "🎓 Education", "💼 Work Experience", "⚙️ Edit Profile"
    ])

    # --- TAB 1: OVERVIEW ---
    with tab_overview:
        col1, col2 = st.columns([1, 3])
        with col1:
            if user[14] and user[14] != "": 
                st.markdown(f'<img src="data:image/png;base64,{user[14]}" width="150" style="border-radius: 10px;">', unsafe_allow_html=True)
            else:
                st.warning("No Profile Image")
        
        with col2:
            st.subheader(user[6] if user[6] else "User Name")
            st.write(f"📧 **Email:** {user[1]}")
            st.write(f"📞 **Mobile:** {user[2]}")
            
            loc_parts = [user[12], user[11], user[10]] 
            clean_loc = ", ".join([str(p) for p in loc_parts if p and str(p).lower() != "none"])
            st.write(f"📍 **Location:** {clean_loc if clean_loc else 'Not Set'}")

    # --- Helper function for safe list indexing ---
    def safe_get(lst, idx, default="N/A"):
        return lst[idx] if len(lst) > idx and lst[idx] else default

    # --- TAB 2: EDUCATION ---
    with tab_edu:
        st.subheader("🎓 Educational History")
        if user[15] and user[15] != "[]":
            try:
                edu_list = json.loads(user[15])
                for i, edu in enumerate(edu_list):
                    with st.container(border=True):
                        # Safely extract all 9 sub-parts
                        inst = safe_get(edu, 0, "Unknown Institution")
                        city = safe_get(edu, 1, "Unknown City")
                        degree = safe_get(edu, 2, "Degree Not Specified")
                        e_type = safe_get(edu, 3, "Type Not Specified")
                        stream = safe_get(edu, 4, "Stream Not Specified")
                        start = safe_get(edu, 5, "Start")
                        end = safe_get(edu, 6, "End")
                        grade = safe_get(edu, 7, "N/A")
                        skills = safe_get(edu, 8, "None Listed")

                        st.markdown(f"#### 🏛️ {inst}")
                        st.markdown(f"**{degree} in {stream}** | 📍 {city}")
                        
                        c1, c2, c3 = st.columns(3)
                        c1.write(f"📅 **Duration:** {start} - {end}")
                        c2.write(f"🏆 **Grade/SGPA:** {grade}")
                        c3.write(f"📚 **Mode:** {e_type}")
                        
                        st.caption(f"**Key Skills Learned:** {skills}")
            except Exception as e:
                st.error(f"Error loading education data: {e}")
                st.code(user[15]) # Shows the raw JSON so you can debug what went wrong
        else:
            st.info("No education data added yet.")

    # --- TAB 3: EXPERIENCE ---
    with tab_exp:
        st.subheader("💼 Professional Experience")
        if user[16] and user[16] != "[]":
            try:
                exp_data = json.loads(user[16])
                for job in exp_data:
                    with st.container(border=True):
                        # Safely extract all 7 sub-parts
                        comp = safe_get(job, 0, "Unknown Company")
                        loc = safe_get(job, 1, "Unknown Location")
                        role = safe_get(job, 2, "Unknown Role")
                        j_type = safe_get(job, 3, "Job Type")
                        ctc = safe_get(job, 4, "Not Disclosed")
                        start = safe_get(job, 5, "Start")
                        end = safe_get(job, 6, "Present")

                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"#### 💼 {role} @ {comp}")
                            st.write(f"📍 {loc} | 🛠️ {j_type}")
                            st.write(f"💰 **Compensation:** {ctc}")
                        with c2:
                            st.write(f"📅 {start} - {end}")
            except Exception as e:
                st.error(f"Error loading experience data: {e}")
                st.code(user[16])
        else:
            st.info("No experience records found.")

    # --- TAB 4: EDIT ---
    with tab_edit:
        st.subheader("Update Your Information")
        with st.form("edit_profile_form"):
            new_name = st.text_input("Full Name", value=user[6])
            new_mob = st.text_input("Mobile", value=user[2])
            
            e_col1, e_col2 = st.columns(2)
            new_city = e_col1.text_input("City", value=user[12])
            new_state = e_col2.text_input("State", value=user[11])
            
            st.info("To update Education/Experience, please use the Profile Builder.")
            
            if st.form_submit_button("Save All Changes"):
                conn.execute('''UPDATE users SET full_name=?, mobile=?, city=?, state=? 
                                WHERE email=?''', (new_name, new_mob, new_city, new_state, user[1]))
                conn.commit()
                st.success("Profile Updated!")
                st.rerun()

    conn.close()
