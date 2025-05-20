import os
import sys
import csv
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add parent directory to path to import from linkedin_scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_scraper import actions
from linkedin_scraper.job_search import JobSearch

def main():
    # Get environment variables
    LINKEDIN_USERNAME = os.environ.get("LINKEDIN_USERNAME")
    LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD")
    SEARCH_TERM = os.environ.get("SEARCH_TERM", "Data Engineer")
    
    # Common geoIds:
    # 90009834 - Poland
    GEOID = int(os.environ.get("LINKEDIN_GEOID", "90009834"))
    
    # New parameter for max pages to scrape
    MAX_PAGES = int(os.environ.get("MAX_PAGES", "3"))
    
    if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
        print("Error: LinkedIn username and password must be set as environment variables")
        sys.exit(1)
    
    # Setup Chrome driver
    chrome_options = Options()
    # Uncomment the following line to run headless
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login to LinkedIn
        print(f"Logging in as {LINKEDIN_USERNAME}...")
        driver.get("https://www.linkedin.com/login")
        actions.login(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        
        # Wait for login to complete
        sleep(3)
        
        # Create JobSearch instance (without scraping by default)
        job_search = JobSearch(driver, scrape=False)
        
        print(f"Searching for {SEARCH_TERM} jobs across multiple pages (max: {MAX_PAGES})...")
        
        # Search for jobs using search_multiple_pages instead of search
        jobs = job_search.search_multiple_pages(
            search_term=SEARCH_TERM, 
            geoid=GEOID, 
            max_pages=MAX_PAGES,
            delay_seconds=3
        )
        
        print(f"Found {len(jobs)} jobs. Saving results...")
        
        # Create timestamp for filenames
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory if it doesn't exist
        output_dir = "job_results"
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare filenames
        csv_filename = f"{output_dir}/{SEARCH_TERM.replace(' ', '_')}_{timestamp}.csv"
        json_filename = f"{output_dir}/{SEARCH_TERM.replace(' ', '_')}_{timestamp}.json"
        
        # Save results to CSV
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["job_title", "company", "location", "posted_date", 
                         "applicant_count", "linkedin_url", "workplace_type", "experience"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for job in jobs:
                writer.writerow({
                    "job_title": job.job_title,
                    "company": job.company,
                    "location": job.location,
                    "posted_date": job.posted_date,
                    "applicant_count": job.applicant_count,
                    "linkedin_url": job.linkedin_url,
                    "workplace_type": job.workplace_type,
                    "experience": job.experience
                })
        
        # Save full job details to JSON
        with open(json_filename, "w", encoding="utf-8") as jsonfile:
            json_data = []
            for job in jobs:
                job_data = {
                    "job_title": job.job_title,
                    "company": job.company,
                    "company_linkedin_url": job.company_linkedin_url,
                    "location": job.location,
                    "posted_date": job.posted_date,
                    "applicant_count": job.applicant_count,
                    "linkedin_url": job.linkedin_url,
                    "workplace_type": job.workplace_type,
                    "experience": job.experience,
                    "job_description": job.job_description
                }
                json_data.append(job_data)
            json.dump(json_data, jsonfile, indent=2)
        
        print(f"Results saved to:")
        print(f"- CSV: {csv_filename}")
        print(f"- JSON: {json_filename}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()