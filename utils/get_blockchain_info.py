import requests
from bs4 import BeautifulSoup

def get_blockchain_info(blockchain: str):
    # beautiful soup is not supporting js which is need to get the site to run correctly so we will need to do web search 
    
    # # check if it is evm
    # blockchain_info = fetch_blockchain_info(blockchain)
    # if blockchain_info != {}:
    #     rpc_endpoints = get_rpc_endpoints(blockchain_info["chain_id"])
    #     # Do something with the rpc_endpoints
    #     blockchain_info["rpc_endpoints"] = rpc_endpoints
    #     return blockchain_info
    # else:
    #     # should do a web search for it and then return the results via a set of agents
        return "call web_search for finding the chain id, native currency, rpc url and encryption curve "
    


def fetch_blockchain_info(blockchain: str):
    url = f"https://chainlist.org/?search={blockchain}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        div = soup.find("div", class_="shadow dark:bg-[#0D0D0D] bg-white p-8 pb-0 rounded-[10px] flex flex-col gap-3 overflow-hidden")
        if div:
            blockchain = div.find("span", class_="text-xl font-semibold whitespace-nowrap overflow-hidden text-ellipsis relative top-[1px] dark:text-[#B3B3B3]").text
            table = div.find("table")
            if table:
                rows = table.find_all("tr")
                chain_id = rows[1].find("td").text.strip()
                currency = rows[1].find_all("td")[1].text.strip()
                return {
                    "blockchain": blockchain,
                    "chain_id": chain_id,
                    "currency": currency,
                    "encryption_curve": "secp256k1"
                }
    return {}


def get_rpc_endpoints(chainId: str):
    url = f"https://chainlist.org/chain/{chainId}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        urls = []
        table = soup.find("table")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                td = row.find("td")
                if td:
                    text = td.get_text(strip=True)
                    urls.append(text)
        return urls
    else:
        return []


