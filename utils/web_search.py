import requests
import json
import requests
from utils.crawler import crawl_page
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from utils.extractor import extract_urls
from config import serper_api_key

def web_search(search_keyword):    
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": search_keyword
    })

    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print("RESPONSE:", response.text)
    return response.text