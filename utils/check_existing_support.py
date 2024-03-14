# # import firebase_admin
# # from firebase_admin import credentials
# # from firebase_admin import firestore

# # Initialize the Firebase Admin SDK
# cred = credentials.Certificate("path/to/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

def get_supported_chains():
    # # Get a Firestore client
    # db = firestore.client()

    # # Reference the "config/supportedChains" collection
    # supported_chains_ref = db.collection("config").document("supportedChains")

    # # Get the document snapshot
    # doc_snapshot = supported_chains_ref.get()

    # # Check if the document exists
    # if doc_snapshot.exists:
    #     # Get the data from the document
    #     data = doc_snapshot.to_dict()
    #     return data
    # else:
    #     return None
    return [
        {
            'name': 'Arbitrum',
            'chainId': 42161
        },
        {
            'name': 'Avalanche',
            'chainId': 43114
        },
        {
            'name': 'Base',
            'chainId': 8453
        },
        {
            'name': 'Binance Smart Chain',
            'chainId': 56
        }, 
        {
            'name': 'DFK',
            'chainId': 53935
        }, 
        {
            'name': 'EOSEVM',
            'chainId': 17777
        }, 
        {
            'name': 'Ethereum',
            'chainId' : 1
        }, 
        {
            'name': 'Fantom',
            'chainId': 250
        },
        {
            'name': 'Flow',
            'chainId': 0
        },
        {
            'name': 'Gnosis',
            'chainId': 100
        }, 
        {
            'name': 'Immutable X',
            'chainId': 42161
        }, 
        {
            'name': 'Klaytn',
            'chainId': 8217
        }, 
        {
            'name': 'Optimism',
            'chainId': 10
        },
        {
            'name': 'Polygon',
            'chainId': 137
        }, 
        {
            'name': 'Solana',
            'chainId': 1399811149
        }, 
        ]

def check_existing_support(chain_id, chain_name):
    supported_chains = get_supported_chains()
    if supported_chains:
        for chain in supported_chains.values():
            if chain.get("chainId") == chain_id or chain.get("name") == chain_name:
                return True
        return False
