import streamlit as st
from job_api_handler import JobAPIHandler
from Functions.mydatabase import get_db

def dashboard():
    st.title("🔍 Job Search Dashboard")
    
    # Instantiate the handler inside the function
    api_handler = JobAPIHandler()
    
    query = st.text_input("Search Role (e.g. Java Developer)", placeholder="Search...")
    
    if st.button("Search"):
        if not query:
            st.warning("Please enter a job title to search.")
            return

        with st.spinner(f"Searching for '{query}' across multiple platforms..."):
            all_jobs = []

            # 1. Fetch from Local SQLite Database first
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT title, company, location, link FROM jobs WHERE LOWER(title) LIKE ?", (f"%{query.lower()}%",))
            db_jobs = cursor.fetchall()
            for job in db_jobs:
                all_jobs.append({'title': job[0], 'company': job[1], 'location': job[2], 'link': job[3], 'source': 'Local DB'})
            conn.close()

            # 2. Fetch from External APIs using your imported handler
            try:
                # Assuming your handler has these methods based on previous context
                all_jobs.extend(api_handler.fetch_adzuna(query))
                all_jobs.extend(api_handler.fetch_jooble(query))
                all_jobs.extend(api_handler.fetch_serpapi(query))
            except Exception as e:
                st.error(f"Error fetching from APIs: {e}")

            # 3. Display Results
            if not all_jobs:
                st.info("No jobs found. Try a different keyword.")
            else:
                st.success(f"Found {len(all_jobs)} jobs!")
                for job in all_jobs:
                    with st.container():
                        # Using a card-like layout
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"### {job.get('title', 'N/A')}")
                            st.write(f"🏢 **{job.get('company', 'Unknown')}** | 📍 {job.get('location', 'Remote')}")
                            if 'source' in job:
                                st.caption(f"Source: {job['source']}")
                        with col2:
                            st.write("##") # Spacing
                            # Open link in a new tab
                            st.link_button("Apply Now", job.get('link', '#'), use_container_width=True)
                        st.divider()
