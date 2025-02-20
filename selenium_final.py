from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_textarea_content(url, wait_time=10):
    """
    Scrapes only the content from textarea tags after waiting for the page to load.
    
    Args:
        url (str): The URL of the webpage to scrape
        wait_time (int): Time to wait in seconds for the page to load
        
    Returns:
        list: List of strings containing text from each textarea
    """
    # Setup Chrome options for WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no GUI)
    
    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)
    
    try:
        # Load the webpage
        driver.get(url)
        
        # Wait for specified time
        time.sleep(wait_time)
        
        # Find all textarea elements
        textareas = driver.find_elements(By.TAG_NAME, 'textarea')
        
        # Extract only the text content from textareas
        textarea_contents = [textarea.get_attribute('value') or textarea.text for textarea in textareas]
        
        return textarea_contents
        
    finally:
        # Always close the browser
        driver.quit()

# Example usage
if __name__ == "__main__":
    url = "https://gitingest.com/ninadw25/FrameFlow"  # Replace with your target URL
    try:
        textarea_texts = scrape_textarea_content(url)
        
        if textarea_texts:
            print("Textarea contents:")
            for text in textarea_texts:
                print(text)
                print("-" * 50)  # Separator between textarea contents
        else:
            print("No textarea content found.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")