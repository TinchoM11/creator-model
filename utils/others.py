from typing import TypedDict
from flask import make_response
import re

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


class BlockchainInfo(TypedDict):
    rpc_url: str | None
    chain_id: str | None
    gas_token: str | None


def extract_blockchain_info_from_response(input_str: str) -> BlockchainInfo:
    """
    Extracts RPC URL, Chain ID, and Gas Token from a complex string that contains JSON-like structures.

    Parameters:
    - input_str (str): The input string containing the information.

    Returns:
    - dict: A dictionary with keys 'rpc_url', 'chain_id', and 'gas_token'.
    """
    # Attempt to find the JSON-like structure within the string
    print("Input String", input_str)
    try:
        rpc_url_match = re.search(r"RPC URL: (https?://[^\s]+)", input_str)
        chain_id_match = re.search(r"Chain ID: (\d+)", input_str)
        gas_token_match = re.search(r"Currency Symbol: (\w+)", input_str)

        rpc_url = rpc_url_match.group(1) if rpc_url_match else None
        chain_id = chain_id_match.group(1) if chain_id_match else None
        gas_token = gas_token_match.group(1) if gas_token_match else None

        return {
            "rpc_url": rpc_url,
            "chain_id": chain_id,
            "gas_token": gas_token
        }
    except Exception as e:
        print("Error:", e)
        return {
            "rpc_url": None,
            "chain_id": None,
            "gas_token": None
        }


def extract_last_typescript_block(bridge_code_messages):
    """
    Extracts the last TypeScript block from the given string.

    Parameters:
    - bridge_code_messages (str): The input string containing potential TypeScript blocks.

    Returns:
    - str or None: The last TypeScript block found, or None if no block is found.
    """
    blocks = []
    start = 0
    while True:
        start = bridge_code_messages.find("```typescript", start)
        if start == -1:
            break  # No more TypeScript blocks

        end = bridge_code_messages.find("```", start + len("```typescript"))
        if end == -1:
            break  # No closing backticks found (unlikely, but just in case)

        # Extract the TypeScript block and add it to the list
        blocks.append(bridge_code_messages[start:end+len("```")])

        # Move past the end of the current block to search for the next one
        start = end + len("```")

    # Return the last TypeScript block found, or None if no blocks were found
    return blocks[-1] + "```" if blocks else None

