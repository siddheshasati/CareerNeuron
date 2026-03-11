import requests

class JobAPIHandler:
    def __init__(self):
        # Replace these with your actual API Keys
        self.ADZUNA_APP_ID = "0e800a8f"
        self.ADZUNA_APP_KEY = "93de394f00aa0f70243e17cc5520225e"
        self.JOOBLE_API_KEY = "b3ba7c3f-605b-4a74-a350-249775a6656d"
        self.SERPAPI_KEY = "4a1505b5b82c797db1e797a7be4b310cc605869c5b09a325a2732c0c4d2a8a97"

    def fetch_adzuna(self, query, location="India"):
        """Fetches jobs from Adzuna API"""
        url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
        params = {
            "app_id": self.ADZUNA_APP_ID,
            "app_key": self.ADZUNA_APP_KEY,
            "results_per_page": 10,
            "what": query,
            "where": location,
            "content-type": "application/json"
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            results = []
            for job in data.get('results', []):
                results.append({
                    "title": job.get('title'),
                    "company": job.get('company', {}).get('display_name'),
                    "location": job.get('location', {}).get('display_name'),
                    "link": job.get('redirect_url')
                })
            return results
        except Exception as e:
            print(f"Adzuna Error: {e}")
            return []

    def fetch_jooble(self, query, location="India"):
        """Fetches jobs from Jooble API"""
        url = f"https://jooble.org/api/{self.JOOBLE_API_KEY}"
        body = {
            "keywords": query,
            "location": location
        }
        try:
            response = requests.post(url, json=body)
            data = response.json()
            results = []
            for job in data.get('jobs', []):
                results.append({
                    "title": job.get('title'),
                    "company": job.get('company', 'Unknown'),
                    "location": job.get('location'),
                    "link": job.get('link')
                })
            return results
        except Exception as e:
            print(f"Jooble Error: {e}")
            return []

    def fetch_serpapi(self, query):
        """Fetches Google Jobs via SerpApi"""
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_jobs",
            "q": query,
            "hl": "en",
            "api_key": self.SERPAPI_KEY
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            results = []
            for job in data.get('jobs_results', []):
                results.append({
                    "title": job.get('title'),
                    "company": job.get('company_name'),
                    "location": job.get('location'),
                    "link": job.get('related_links', [{}])[0].get('link', '#')
                })
            return results
        except Exception as e:
            print(f"SerpApi Error: {e}")
            return []