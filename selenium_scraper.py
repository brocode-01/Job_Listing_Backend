import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import logging
from fake_useragent import UserAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize Chrome driver with anti-detection measures"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Anti-detection settings
        ua = UserAgent()
        chrome_options.add_argument(f'user-agent={ua.random}')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Additional stealth settings
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.managed_default_content_settings.images": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("window.navigator.chrome = { runtime: {} };")
            self.driver.implicitly_wait(15)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def human_like_delay(self, min_delay=2, max_delay=5):
        """Add random delay to simulate human behavior"""
        time.sleep(random.uniform(min_delay, max_delay))
    
    def scroll_page(self):
        """Simulate human-like scrolling behavior"""
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            current_position = 0
            
            while current_position < total_height:
                scroll_amount = random.randint(100, 400)
                current_position += scroll_amount
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                self.human_like_delay(0.5, 1.5)
                
                if random.random() < 0.2:
                    current_position -= random.randint(50, 200)
                    self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                    self.human_like_delay(0.5, 1)
            
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human_like_delay(1, 2)
        except Exception as e:
            logger.warning(f"Error during scrolling: {e}")
    
    def scrape_jobs(self, search_term="software engineer", location="", max_pages=1):
        """Main method to scrape jobs"""
        try:
            logger.info(f"Starting job scraping for: {search_term}")
            jobs = self.scrape_linkedin_jobs(search_term, location, max_pages)
            
            if not jobs:
                logger.warning("No jobs found on LinkedIn")
                return []
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return []
    
    def _find_linkedin_job_cards(self, limit=5):
        """Find LinkedIn job cards with limit"""
        selectors = [
            '.jobs-search__results-list > li',
            '.job-search-card',
            '.jobs-search-results__list-item'
        ]
        
        for selector in selectors:
            try:
                # Wait for at least 'limit' number of cards to be present
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"{selector}:nth-child(-n+{limit})"))
                )
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if cards:
                    cards = cards[:limit]  # Ensure we only get the number we need
                    logger.info(f"Found {len(cards)} job cards")
                    return cards
            except TimeoutException:
                continue
        
        return None

    def _extract_linkedin_jobs(self, cards):
        """Extract job data from LinkedIn cards"""
        jobs = []
        for i, card in enumerate(cards, 1):
            try:
                # Minimal scroll for just the current card
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", 
                    card
                )
                
                job_data = {}
                
                # Extract essential data first
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, 'h3.base-search-card__title, .job-search-card__title')
                    job_data['title'] = title_elem.text.strip()
                    
                    company_elem = card.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle, .job-search-card__company-name')
                    job_data['company'] = company_elem.text.strip()
                    
                    if not (job_data['title'] and job_data['company']):
                        continue
                        
                except (NoSuchElementException, AttributeError):
                    continue
        
                # Extract location
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__location, span.job-search-card__location')
                    job_data['location'] = location_elem.text.strip()
                except:
                    job_data['location'] = "Location Not Specified"
                
                # Extract link
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, 'a.base-card__full-link, a.job-search-card__link')
                    job_data['application_url'] = link_elem.get_attribute('href')
                except:
                    job_data['application_url'] = ""
                
                # Set default values for optional fields
                job_data.update({
                    'description': "Click the application URL to view the full job description on LinkedIn.",
                    'job_type': "Full-time",
                    'experience_level': self._extract_experience_level(job_data['title']),
                    'salary': "",
                    'posted_date': ""
                })
                
                # Try to get optional data without causing delays
                try:
                    date_elem = card.find_element(By.CSS_SELECTOR, 'time.job-search-card__listdate')
                    job_data['posted_date'] = date_elem.get_attribute('datetime')
                except:
                    pass
                
                try:
                    salary_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__salary-info')
                    job_data['salary'] = salary_elem.text.strip()
                except:
                    pass
                
                jobs.append(job_data)
                logger.info(f"Extracted job {i}: {job_data['title']} at {job_data['company']}")
                
                # Minimal delay between extractions
                if i < len(cards):
                    time.sleep(0.5)
                
        except Exception as e:
                logger.warning(f"Error extracting job {i}: {e}")
                continue
        
        return jobs
    
    def _get_job_priority_score(self, job):
        """Calculate priority score for job sorting"""
        score = 0
        title_lower = job.get('title', '').lower()
        
        # Prioritize by experience level
        if any(senior in title_lower for senior in ['senior', 'sr.', 'lead', 'principal', 'staff', 'architect']):
            score += 5
        elif any(mid in title_lower for mid in ['mid', 'intermediate', 'software engineer II']):
            score += 3
        elif any(junior in title_lower for junior in ['junior', 'jr.', 'entry', 'intern', 'internship']):
            score -= 2
            
        # Penalize internships and temporary positions
        if any(term in title_lower for term in ['intern', 'internship', 'temporary', 'contract']):
            score -= 3
            
        # Boost for key technologies
        tech_keywords = ['python', 'javascript', 'react', 'node', 'aws', 'cloud', 'full stack', 'fullstack']
        score += sum(2 for tech in tech_keywords if tech in title_lower)
        
        # Boost for remote positions
        if 'remote' in job.get('location', '').lower():
            score += 2
            
        return score

    def _extract_experience_level(self, title):
        """Extract experience level from job title"""
        title_lower = title.lower()
        
        # Senior level positions
        if any(senior in title_lower for senior in ['senior', 'sr.', 'lead', 'principal', 'staff', 'architect']):
            return 'Senior'
        
        # Mid level positions
        elif any(mid in title_lower for mid in ['mid', 'intermediate', 'software engineer II', 'software engineer 2']):
            return 'Mid'
        
        # Junior level positions
        elif any(junior in title_lower for junior in ['junior', 'jr.', 'entry', 'intern', 'internship']):
            return 'Entry'
        
        # Default to Mid if no specific level found
        else:
            return 'Mid'
            
    def scrape_linkedin_jobs(self, search_term="software engineer", location="", max_pages=1):
        """Scrape jobs from LinkedIn"""
        jobs = []
        
        try:
            # Format the URL with filters for better initial results
            search_encoded = search_term.replace(' ', '%20')
            location_encoded = location.replace(' ', '%20') if location else "worldwide"
            
            # Add filters to get most relevant results first
            filters = [
                'f_TPR=r86400',        # Last 24 hours
                'f_JT=F',              # Full-time jobs only
                'f_E=2%2C3%2C4',       # Mid-Senior level (2=Mid, 3=Senior, 4=Executive)
                'sortBy=R',            # Most relevant first
                'position=1',          # Start position
                'pageNum=0',           # First page
                'f_AL=true'           # Easy apply jobs
            ]
            
            base_url = f"https://www.linkedin.com/jobs/search/?keywords={search_encoded}&location={location_encoded}&{'&'.join(filters)}"
            
            logger.info(f"Accessing LinkedIn Jobs: {base_url}")
            self.driver.get(base_url)
            
            # Short delay for initial load
            self.human_like_delay(2, 3)
            
            # Wait for job cards to load with a specific limit
            job_cards = self._find_linkedin_job_cards(limit=5)
            if not job_cards:
                logger.warning("No job cards found")
                return []
            
            # Process only the first 5 job cards
            jobs.extend(self._extract_linkedin_jobs(job_cards[:5]))
            
            if not jobs:
                logger.warning("Failed to extract any jobs")
                return []
            
            # Sort jobs by priority
            sorted_jobs = sorted(jobs, 
                key=lambda x: (
                    self._get_job_priority_score(x),
                    x.get('salary', '') != '',  # Prioritize jobs with salary info
                    len(x.get('description', '')) > 100  # Prioritize detailed descriptions
                ),
                reverse=True
            )[:5]
            
            return sorted_jobs
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
            return []
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser driver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
    
    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.close()

# Test the scraper
if __name__ == "__main__":
    scraper = JobScraper(headless=True)  # Set to False for debugging
    
    try:
        # Test with sample data first
        print("Testing with sample data...")
        jobs = scraper.scrape_jobs("python developer", "california", use_sample=False, max_pages=1)
        
        print(f"\nScraped {len(jobs)} jobs:")
        for i, job in enumerate(jobs[:5], 1):  # Show first 5 jobs
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Salary: {job['salary']}")
            print(f"   Type: {job['job_type']}")
            print(f"   Level: {job['experience_level']}")
            if job['application_url']:
                print(f"   URL: {job['application_url'][:50]}...")
    
    finally:
        scraper.close()