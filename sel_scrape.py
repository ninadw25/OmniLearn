from selenium import webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import time
import os

def get_file_name_from_url(url):
    """Extract the last two parts of the URL path and create a filename."""
    path_parts = urlparse(url).path.strip('/').split('/')
    last_two_parts = path_parts[-2:]
    return f"{'-'.join(last_two_parts)}.txt"

def scrape_textarea_content(url, wait_time=10):
    """
    Scrapes content from textarea tags and saves to a file.
    
    Args:
        url (str): The URL of the webpage to scrape
        wait_time (int): Time to wait in seconds for the page to load
        
    Returns:
        tuple: (list of textarea contents, filename where content was saved)
    """
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
        
        # Create 'scraped_content' directory if it doesn't exist
        os.makedirs('scraped_content', exist_ok=True)
        
        # Save content to file
        filepath = os.path.join('scraped_content', filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, content in enumerate(textarea_contents, 1):
                f.write(f"Content from textarea {i}:\n")
                f.write("=" * 50 + "\n")
                f.write(content + "\n")
                f.write("=" * 50 + "\n\n")
        
        return textarea_contents, filepath
        
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://gitingest.com/mannaandpoem/OpenManus"  # Replace with your target URL
    # url = "https://github.com/ninadw25/OmniLearn"  # Replace with your target URL
    try:
        textarea_texts, saved_file = scrape_textarea_content(url)
        
        if textarea_texts:
            print(f"Content has been scraped and saved to: {saved_file}")
            print("\nTextarea contents:")
            for text in textarea_texts:
                print("-" * 50)
                print(text)
        else:
            print("No textarea content found.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")