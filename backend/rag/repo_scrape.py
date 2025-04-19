from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import time
import os
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

def convert_github_to_gitingest(url):
    """Convert GitHub URLs to GitIngest URLs."""
    logger.debug(f"Converting URL: {url}")
    if 'github.com' in url:
        converted_url = url.replace('github.com', 'gitingest.com')
        logger.info(f"Converted GitHub URL to GitIngest: {converted_url}")
        return converted_url
    return url

def get_file_name_from_url(url):
    """Extract the last two parts of the URL path and create a filename."""
    path_parts = urlparse(url).path.strip('/').split('/')
    last_two_parts = path_parts[-2:]
    return f"{'-'.join(last_two_parts)}.txt"

def scrape_textarea_content(url, wait_time=10, output_dir=None):
    """
    Scrapes content from textarea tags and saves to a file.
    
    Args:
        url (str): The URL of the webpage to scrape
        wait_time (int): Time to wait in seconds for the page to load
        output_dir (str): Directory where to save the scraped content
        
    Returns:
        tuple: (list of textarea contents, filename where content was saved)
    """
    logger.info(f"Starting scraping process for URL: {url}")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(wait_time)
        
        textareas = driver.find_elements(By.TAG_NAME, 'textarea')
        textarea_contents = [textarea.get_attribute('value') or textarea.text for textarea in textareas]
        
        # Generate filename from URL
        filename = get_file_name_from_url(url)
        
        # Use provided output directory or default to 'scraped_content'
        if output_dir is None:
            output_dir = 'scraped_content'
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save content to file
        filepath = os.path.join(output_dir, filename)
        logger.info(f"Saving content to: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
            for i, content in enumerate(textarea_contents, 1):
                f.write(f"Content from textarea {i}:\n")
                f.write("=" * 50 + "\n")
                f.write(content + "\n")
                f.write("=" * 50 + "\n\n")
        
        return textarea_contents, filepath
        
    finally:
        driver.quit()

if __name__ == "__main__":
    logger.info("Starting repository scraping script")
    url = input("Enter the URL to scrape (GitHub URLs will be converted to GitIngest): ")
    
    try:
        textarea_texts, saved_file = scrape_textarea_content(url)
        
        if textarea_texts:
            logger.info(f"Scraping completed successfully. Content saved to: {saved_file}")
            logger.debug(f"Number of textarea contents: {len(textarea_texts)}")
        else:
            logger.warning("No textarea content found in the scraped page")
            
    except Exception as e:
        logger.error(f"Script execution failed: {str(e)}", exc_info=True)