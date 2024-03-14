import requests


def get_all_bridges(blockchain: str):
    blockchain = blockchain.lower()
    print("BLOCKCHAIN:", blockchain)
    url = "https://bridges.llama.fi/bridges"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)
    # matching_bridges = []
    bridges = response.json().get('bridges', [])
    print("BRIDGES:", bridges)
    for bridge in bridges:
        if blockchain in (chain.lower() for chain in bridge.get('chains', [])):
            return(bridge)
    
    return None

def get_all_dexes(blockchain: str):
    # make sure blockchain is lowercase and trimmed of whitespace
    blockchain = blockchain.lower()
    blockchain = blockchain.strip()
    print("BLOCKCHAIN:", blockchain)

    url = f"https://api.llama.fi/overview/dexs/{blockchain}?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyVolume"

    payload = {}
    headers = {
        "accept": "*/*",
        "Host": "api.llama.fi",
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    protocol_list = response.json().get('protocols', [])

    # Filter out protocols with None values in dailyVolume
    protocol_list = [protocol for protocol in protocol_list if protocol.get('dailyVolume') is not None]

    # Sort protocol_list by "dailyVolume"
    if len(protocol_list) > 0:
        protocol_list = sorted(protocol_list, key=lambda x: x.get('dailyVolume', 0), reverse=True)
        return protocol_list[0]
    return None