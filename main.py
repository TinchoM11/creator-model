from flask import Flask, jsonify, request
from agents.chain_agent import get_chain_agent_response
from agents.bridge_code_agent import generate_code_for_bridge
from agents.dex_code_agent import generate_code_for_dex
from agents.transfer_agents import generate_code_for_transfer
from utils.get_links_from_url import get_links_from_url
import asyncio
from utils.others import _build_cors_preflight_response, _corsify_actual_response, extract_blockchain_info_from_response, extract_last_typescript_block
import os

app = Flask(__name__)

@app.route('/integration', methods=['POST', 'OPTIONS'])
def call_ai_with_request():
    # cors preflight
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == "POST":  # The actual request following the preflight
        data = request.get_json()
        message = data.get('message')
        # get chain information
        ai_message = get_chain_agent_response(message)
        chain_info = extract_blockchain_info_from_response(str(ai_message))

        # generate code for the transfer
        # Comment out for now just testing
        transfer_code_messages = generate_code_for_transfer(str(chain_info['chain_id']), str(chain_info['rpc_url']))
        transfer_typescript_block = extract_last_typescript_block(
            str(transfer_code_messages))

        # get the urls for the dex
        dex_urls = ["https://docs.uniswap.org/sdk/v3/overview"]

        # crawl the page
        result_from_links = asyncio.run(get_links_from_url(dex_urls[0]))

        # generate code for the dex
        dex_code_messages = generate_code_for_dex(result_from_links, dex_urls[0], str(
            chain_info['rpc_url']), str(chain_info['chain_id']))
        dex_typescript_block = extract_last_typescript_block(
            str(dex_code_messages))
        # dex_typescript_block = "No DEX code generated"

        bridge_urls = [
            "https://docs.li.fi/integrate-li.fi-js-sdk/request-a-route"]


        # generate code for the bridge
        bridge_code_messages = generate_code_for_bridge(result_from_links, bridge_urls[0], str(chain_info['chain_id']), str(chain_info['rpc_url']))
        bridge_typescript_block = extract_last_typescript_block(str(bridge_code_messages))
        # bridge_typescript_block = "No bridge code generated"

        response = jsonify({
            'chain_info': str(chain_info),
            "transfer_code_messages": transfer_typescript_block,
            'dex_code_messages': dex_typescript_block,
            'bridge_code_messages': bridge_typescript_block
        })
        return _corsify_actual_response(response)
    else:
        raise RuntimeError(
            "Weird - don't know how to handle method {}".format(request.method))

@app.route('/integration/manual', methods=['POST', 'OPTIONS'])
def process_urls():
    # cors preflight
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    elif request.method == "POST":  # The actual request following the preflight
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    message = data.get('message')
    dex_url = data.get('dex_url')
    bridge_url = data.get('bridge_url')
    if not dex_url or not bridge_url:
        return jsonify({"error": "Both 'dex_url' and 'bridge_url' are required"}), 400

    # get chain information
    ai_message = get_chain_agent_response(message)
    chain_info = extract_blockchain_info_from_response(str(ai_message))

    # generate code for the transfer
    transfer_code_messages = generate_code_for_transfer(
        str(chain_info['rpc_url']), str(chain_info['chain_id']))
    transfer_typescript_block = extract_last_typescript_block(
        str(transfer_code_messages))
    # Process DEX URL
    try:
        dex_result_from_links = asyncio.run(get_links_from_url(dex_url))
        dex_code_messages = generate_code_for_dex(dex_result_from_links, dex_url, str(
            chain_info['rpc_url']), str(chain_info['chain_id']))
        dex_typescript_block = extract_last_typescript_block(dex_code_messages)
    except Exception as e:
        dex_typescript_block = f"Error processing DEX URL: {str(e)}"

    # Process Bridge URL
    try:
        bridge_result_from_links = asyncio.run(get_links_from_url(bridge_url))
        bridge_code_messages = generate_code_for_bridge(
            bridge_result_from_links, bridge_url, str(chain_info['chain_id']), str(chain_info['rpc_url']))
        bridge_typescript_block = extract_last_typescript_block(
            bridge_code_messages)
    except Exception as e:
        bridge_typescript_block = f"Error processing Bridge URL: {str(e)}"

    # Construct and return the response
    response = jsonify({
        'chain_info': str(chain_info),
        "transfer_code_messages": transfer_typescript_block,
        'dex_code_messages': dex_typescript_block,
        'bridge_code_messages': bridge_typescript_block
    })
    return _corsify_actual_response(response)

@app.route('/integration/chain-info', methods=['POST'])
def get_chain_info():
    """
    Endpoint to retrieve blockchain information based on the provided message.
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        message = data.get('message')
        if not message:
            return jsonify({"error": "Message is required"}), 400

        ai_message = get_chain_agent_response(message)
        chain_info = extract_blockchain_info_from_response(str(ai_message))
        return jsonify(chain_info), 200
    except Exception as e:
        # Log the error for debugging purposes
        # e.g., app.logger.error(f"Error retrieving chain info: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@app.route('/integration/transfer', methods=['POST'])
def generate_transfer_code():
    """
    Endpoint to generate transfer code after retrieving chain information.
    """
    chain_info = request.get_json()
    if not chain_info:
        return jsonify({"error": "Chain information is required"}), 400

    transfer_code_messages = generate_code_for_transfer(
        chain_info.get('chain_id'), chain_info.get('rpc_url'))
    transfer_typescript_block = extract_last_typescript_block(
        str(transfer_code_messages))
    return jsonify({"transfer_code_messages": transfer_typescript_block})

@app.route('/integration/swap', methods=['POST'])
def generate_swap_code():
    """
    Endpoint to generate swap code for DEX after retrieving chain information.
    """
    data = request.get_json()
    chain_info = data.get('chain_info')
    dex_url = data.get('dex_url') or "https://docs.uniswap.org/sdk/v3/overview"

    if not chain_info:
        return jsonify({"error": "Chain information is required"}), 400

    try:
        result_from_links = asyncio.run(get_links_from_url(dex_url))
        dex_code_messages = generate_code_for_dex(
            result_from_links, dex_url, chain_info.get('rpc_url'), chain_info.get('chain_id'))
        dex_typescript_block = extract_last_typescript_block(str(dex_code_messages))
    except Exception as e:
        dex_typescript_block = f"Error processing DEX URL: {str(e)}"

    return jsonify({'dex_code_messages': dex_typescript_block})

@app.route('/integration/bridge', methods=['POST'])
def generate_route_code():
    """
    Endpoint to generate routing code for bridges after retrieving chain information.
    """
    data = request.get_json()
    chain_info = data.get('chain_info')
    bridge_url = data.get('bridge_url') or "https://docs.li.fi/integrate-li.fi-js-sdk/request-a-route"

    if not chain_info:
        return jsonify({"error": "Chain information is required"}), 400

    try:
        result_from_links = asyncio.run(get_links_from_url(bridge_url))
        bridge_code_messages = generate_code_for_bridge(
            result_from_links, bridge_url, chain_info.get('chain_id'), chain_info.get('rpc_url'))
        bridge_typescript_block = extract_last_typescript_block(str(bridge_code_messages))
    except Exception as e:
        bridge_typescript_block = f"Error processing Bridge URL: {str(e)}"

    return jsonify({'bridge_code_messages': bridge_typescript_block})


@app.route('/health')
def health():
    return "OK"


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
 