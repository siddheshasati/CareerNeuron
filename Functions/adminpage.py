import streamlit as st
import requests
from Functions.mydatabase import get_db
from bs4 import BeautifulSoup

def admin_page():
    st.title("🛡️ Admin Panel")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Manual Job Posting")
        title = st.text_input("Job Title")
        comp = st.text_input("Company")
        link = st.text_input("Job Link")
        if st.button("Post Job"):
            if title and comp and link:
                conn = get_db()
                conn.execute("INSERT INTO jobs (title, company, location, link) VALUES (?,?,?,?)", 
                             (title, comp, "Remote", link))
                conn.commit()
                st.success(f"Added {title} to Database!")
            else:
                st.warning("Please fill all fields.")
            
    with col2:
        st.subheader("System Pipeline")
        st.write("Click below to fetch live jobs from the web and refresh the database.")
        
        if st.button("🚀 Run Live Web Scraper"):
            url = "https://realpython.github.io/fake-jobs/" #this is just dummy, we are using actual APIs of real time jobs data
            
            with st.spinner("Connecting to data source..."):
                try:
                    # 1. Fetch Web Data
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, "html.parser")
                    job_elements = soup.find_all("div", class_="card-content")

                    # 2. Database Cleanup & Update
                    conn = get_db()
                    cursor = conn.cursor()
                    
                    # Clear existing jobs to prevent duplicates
                    cursor.execute("DELETE FROM jobs")
                    
                    count = 0
                    for job in job_elements:
                        j_title = job.find("h2", class_="title").text.strip()
                        j_company = job.find("h3", class_="company").text.strip()
                        j_location = job.find("p", class_="location").text.strip()
                        j_link = job.find_all("a")[1]["href"]

                        cursor.execute("INSERT INTO jobs (title, company, location, link) VALUES (?, ?, ?, ?)",
                                       (j_title, j_company, j_location, j_link))
                        count += 1

                    conn.commit()
                    st.success(f"Pipeline Complete: Synced {count} live jobs!")
                    
                except Exception as e:
                    st.error(f"Scraper Error: {e}")