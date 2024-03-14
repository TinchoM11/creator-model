import requests
from bs4 import BeautifulSoup
import json
import requests
from config import brwoserless_api_key


def web_scraping(url: str):
        #scrape website, and also will summarize the content based on objective if the content is too large
    #objective is the original objective & task that user give to the agent, url is the url of the website to be scraped

    print("Scraping website...")
    # Define the headers for the request
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # Define the data to be sent in the request
    data = {
        "url": url        
    }

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    response = requests.post(f"https://chrome.browserless.io/content?token={brwoserless_api_key}", headers=headers, data=data_json)
    
    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print("CONTENTT:", text)
        # if len(text) > 10000:
        #     output = summary(objective,text)
        #     return output
        # else:
        return text
    else:
        print(f"HTTP request failed with status code {response.status_code}")            
