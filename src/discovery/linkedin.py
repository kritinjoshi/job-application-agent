import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters

class JobScraper:
    def __init__(self):
        self.jobs = []
        logging.basicConfig(level=logging.INFO)

    def scrape_jobs(self, keywords, location, limit=5):
        self.jobs = []
        
        def on_data(data: EventData):
            print(f"Found Job: [{data.title}] at {data.company}")
            self.jobs.append({
                "title": data.title,
                "company": data.company,
                "link": data.link,
                "description": data.description
            })

        def on_error(error):
            print(f"Error scraping: {error}")

        # Init scraper (using anonymous browsing, no login required)
        scraper = LinkedinScraper(
            chrome_executable_path=None, 
            chrome_binary_location=None, 
            chrome_options=None, 
            headless=True,
            max_workers=1,
            slow_mo=1.5, 
            page_load_timeout=40000
        )

        scraper.on(Events.DATA, on_data)
        scraper.on(Events.ERROR, on_error)

        queries = [
            Query(
                query=keywords,
                options=QueryOptions(
                    locations=[location],
                    apply_link=True,
                    skip_promoted_jobs=True,
                    page_offset=0,
                    limit=limit,
                    filters=QueryFilters(
                        company_jobs_url=None,
                        relevance=RelevanceFilters.RECENT,
                        time=TimeFilters.MONTH,
                        type=[TypeFilters.FULL_TIME],
                        on_site_or_remote=None,
                        experience=None,
                        base_salary=None
                    )
                )
            )
        ]

        print(f"Starting LinkedIn scraper for '{keywords}' in '{location}'...")
        scraper.run(queries)
        return self.jobs

    def _on_data(self, data: EventData):
        print(f"Found Job: [{data.title}] at {data.company}")
        self.jobs.append({
            "title": data.title,
            "company": data.company,
            "link": data.link,
            "description": data.description
        })

    def _on_error(self, error):
        print(f"Error scraping: {error}")
