import requests
from bs4 import BeautifulSoup

chain_list = []

def checkChainList(blockchain):
    # fetch website from https://chainlist.org/?search={blockchain}
    # find the chain id, native currency, rpc url and assume encryption curve because of evm
    return {"chainId": 1, "nativeCurrency": "ETH", "rpcUrl": "https://mainnet.infura.io/v3/8e0d2b6b4a0b4b0d9b7b3f0b0f0b0f0b", "encryptionCurve": "secp256k1"}

def checkChainList(blockchain):
    # fetch website from https://chainlist.org/?search={blockchain}
    url = f"https://chainlist.org/?search={blockchain}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # scrape the chain id, native currency, rpc url, and encryption curve
    chain_id = soup.find("span", class_="chain-id").text
    native_currency = soup.find("span", class_="native-currency").text
    rpc_url = soup.find("span", class_="rpc-url").text
    encryption_curve = soup.find("span", class_="encryption-curve").text
    
    return {"chainId": chain_id, "nativeCurrency": native_currency, "rpcUrl": rpc_url, "encryptionCurve": encryption_curve}
