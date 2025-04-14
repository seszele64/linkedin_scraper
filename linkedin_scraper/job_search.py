import os
from typing import List
from time import sleep
import urllib.parse
import time

from .objects import Scraper
from . import constants as c
from .jobs import Job

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


class JobSearch(Scraper):
    AREAS = ["recommended_jobs", None, "still_hiring", "more_jobs"]

    def __init__(
        self,
        driver,
        base_url="https://www.linkedin.com/jobs/",
        close_on_complete=False,
        scrape=True,
        scrape_recommended_jobs=True,
    ):
        super().__init__()
        self.driver = driver
        self.base_url = base_url

        if scrape:
            self.scrape(close_on_complete, scrape_recommended_jobs)

    def scrape(self, close_on_complete=True, scrape_recommended_jobs=True):
        if self.is_signed_in():
            self.scrape_logged_in(
                close_on_complete=close_on_complete,
                scrape_recommended_jobs=scrape_recommended_jobs,
            )
        else:
            raise NotImplemented("This part is not implemented yet")

    def _extract_clean_job_url(self, full_url):
        """
        Extract a clean LinkedIn job URL from the full URL.
        
        Args:
            full_url (str): The full URL from the job link element
            
        Returns:
            str: A clean LinkedIn job URL in the format https://www.linkedin.com/jobs/view/{job_id}
        """
        try:
            # Extract job ID from the URL
            if '/jobs/view/' in full_url:
                job_id_section = full_url.split('/jobs/view/')[1]
                job_id = job_id_section.split('/')[0]
                
                # Remove query parameters if present
                if '?' in job_id:
                    job_id = job_id.split('?')[0]
                    
                return f"https://www.linkedin.com/jobs/view/{job_id}"
            else:
                # Fallback to the original URL if it doesn't match the expected pattern
                return full_url
        except (IndexError, AttributeError):
            # In case of any parsing error, return the original URL
            print(f"Warning: Could not parse job URL: {full_url}")
            return full_url

    def scrape_job_card(self, base_element) -> Job:
        job_div = self.wait_for_element_to_load(
            name="artdeco-entity-lockup__title", base=base_element
        )
        base_element.click()
        job_title = job_div.text.strip()
        
        # Extract the job ID path and create a clean LinkedIn URL
        linkedin_url = self._extract_clean_job_url(job_div.find_element(By.TAG_NAME, "a").get_attribute("href"))

        company = base_element.find_element(
            By.CLASS_NAME, "artdeco-entity-lockup__subtitle"
        ).text
        
        company_linkedin_url = self.driver.find_element(
            By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name"
        ).find_element(By.TAG_NAME, "a").get_attribute("href")

        posted_date = self.driver.find_element(
            By.CLASS_NAME, "job-details-jobs-unified-top-card__primary-description-container"
        ).find_elements(
            By.CLASS_NAME, "tvm__text--low-emphasis"
        )[2].text.strip()

        applicant_count = self.driver.find_element(
            By.CLASS_NAME, "job-details-jobs-unified-top-card__primary-description-container"
        ).find_elements(
            By.CLASS_NAME, "tvm__text--low-emphasis"
        )[4].text.strip()

        # Get the job insights text
        job_insight_element = self.driver.find_element(
            By.CLASS_NAME, "job-details-jobs-unified-top-card__job-insight"
        )
        job_insight_text = job_insight_element.text
        
        # Find workplace type in the text
        workplace_type = "Unknown"
        for wt in c.WORKPLACE_TYPES:
            if wt in job_insight_text:
                workplace_type = wt
                break
                
        # Find experience level in the text
        experience = "Unknown"
        for exp in c.EXPERIENCE_LEVELS:
            if exp in job_insight_text:
                experience = exp
                break

        location = base_element.find_element(
            By.CLASS_NAME, "job-card-container__metadata-wrapper"
        ).text
        job_descriptions = self.driver.find_element(By.ID, "job-details").text
        job = Job(
            linkedin_url=linkedin_url,
            job_title=job_title,
            company=company,
            company_linkedin_url=company_linkedin_url,
            location=location,
            posted_date=posted_date,
            applicant_count=applicant_count,
            job_description=job_descriptions,
            scrape=False,
            workplace_type=workplace_type,
            experience=experience,
            driver=self.driver,
        )
        return job

    def scrape_logged_in(self, close_on_complete=True, scrape_recommended_jobs=True):
        driver = self.driver
        driver.get(self.base_url)
        if scrape_recommended_jobs:
            self.focus()
            sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)
            job_area = self.wait_for_element_to_load(
                name="scaffold-finite-scroll__content"
            )
            areas = self.wait_for_all_elements_to_load(
                name="artdeco-card", base=job_area
            )
            for i, area in enumerate(areas):
                area_name = self.AREAS[i]
                if not area_name:
                    continue
                area_results = []
                for job_posting in area.find_elements_by_class_name(
                    "jobs-job-board-list__item"
                ):
                    job = self.scrape_job_card(job_posting)
                    area_results.append(job)
                setattr(self, area_name, area_results)
        return

    def scroll_to_bottom_job_list(self, job_listing_class_name):
        self.scroll_class_name_element_to_page_percent(job_listing_class_name, 0.3)
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)

        self.scroll_class_name_element_to_page_percent(job_listing_class_name, 0.6)
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)

        self.scroll_class_name_element_to_page_percent(job_listing_class_name, 1)
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)

    def search(self, search_term: str, geoid: int, current_page_index: int = 1) -> List[Job]:
        # Build URL with pagination parameter if needed
        start_value = current_page_index * 24
        url_params = f"keywords={urllib.parse.quote(search_term)}&geoId={geoid}&refresh=true"
        if current_page_index > 1:
            url_params += f"&start={start_value}"
            
        url = os.path.join(self.base_url, "search") + f"?{url_params}"
        self.driver.get(url)
        self.scroll_to_bottom()
        self.focus()
        sleep(self.WAIT_FOR_ELEMENT_TIMEOUT)

        job_listing_class_name = "scaffold-layout__list"
        job_listing = self.wait_for_element_to_load(name=job_listing_class_name)
        job_listing = job_listing.find_element(By.XPATH, "./div[1]")
        job_listing_class_name = str(job_listing.get_attribute("class")).replace("\n", "")
        print(f"Class name of the first div: {job_listing_class_name}")
        self.scroll_to_bottom_job_list(job_listing_class_name)

        job_results = []
        while True:
            job_cards = self.wait_for_all_elements_to_load(
                name="job-card-list", base=job_listing
            )
            for job_card in job_cards:
                try:
                    job = self.scrape_job_card(job_card)
                    job_results.append(job)
                except Exception as e:
                    # Handle the exception here
                    print(f"Error parsing job card: {e}")
                time.sleep(5)
            try:
                next_page_button = self.driver.find_element(
                    By.XPATH,
                    # "//span[contains(@class, 'artdeco-button__text') and (contains(., 'Next') or contains(., 'Suivant'))]",
                    # "//div[@class='pagination p4']/span[contains(@class, 'artdeco-button__text') and (contains(., 'Next') or contains(., 'Suivant'))]",
                    "//div[contains(@class, 'jobs-search-pagination') and contains(@class, 'p4')]/button[contains(@class, 'artdeco-button') and .//*[contains(@class, 'artdeco-button__text') and (text()='Next' or text()='Suivant')]]",
                )
                next_page_button.click()
                # Wait for at least one job card to load on the new page
                self.wait_for_element_to_load(
                    by=By.CLASS_NAME, name="job-card-list", base=job_listing
                )
                self.scroll_to_bottom_job_list(job_listing_class_name)
            except NoSuchElementException:
                # If the "Next" button is not found, we are on the last page
                break

        return job_results
