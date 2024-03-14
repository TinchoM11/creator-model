
from dotenv import load_dotenv
from autogen import UserProxyAgent
import autogen
from utils.web_scrape import web_scraping
from config import config_list

def termination_msg(x): return isinstance(
    x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()


def generate_code_for_transfer(chain_id: str, rpc_url: str):
    user_system_message = f"""Create typescript code to send a transaction using ethers.js and rpc: {rpc_url} provided.
    Don't be appraisal in your response.
    The code must be able to transfer native tokens or ERC20 tokens.
    It must wait until the transaction is mined and then display the transaction hash and the transaction receipt.
    Construct the code as cleans as possible.
    Reply TERMINATE when we have the code to send the transaction is made."""
    # Create user proxy agent
    user_proxy = UserProxyAgent(name="user_proxy",
                                is_termination_msg=termination_msg,
                                human_input_mode="NEVER",
                                system_message=user_system_message,
                                code_execution_config=False,
                                )

    coder_system_message = f"""You are a senior typescript engineer expert in blockchain development and decentralized exchange integrations. Your main task is to implement transaction sending functionality using ethers.js library and rpc: {rpc_url} provided.
    In the code, the amount to send, the recipient address and the private key will be received by props.
    THE CODE SHOULD BE ABLE TO TRANSER NATIVE TOKENS OR ERC20 TOKENS.
    IF IT'S AN ERC20, REMEMBER THAT YOU SHOULD PARSE THE AMOUNT WITH THE CORRESPONDING DECIMALS OF THE TOKEN.
    ONLY SEND CODE. WITHOUT DESCRIPTION OR CONTEXT. YOU SHOULD ONLY RESPONSE CODE.
    EVERY CODE SHOULD HAVE ALL THE FUNCTIONS, YOU CAN'T SEND JUST 1 FUNCTION.
    If you declare ERC20 ABI, it must have at least name, decimals, and symbol, balanceOf and transfer functions
    After sending the code, write the word TERMINATE to end the conversation.
    FUNCTIONS TO INCLUDE:
    1. Check balance of sender. If balance is below transfer amount throw an error.
    2. Transfer function
    3. After transfering, wait until the transaction is mined
    4. Get and Display the transaction hash and the transaction receipt.
    Testing and Documentation is not required.
    You MUST NEVER send a code with "TODO" or "PENDING" or "// Implement" parts. COMPLETE ALL THE CODE. IT'S AN ORDER.
    ALWAYS send the COMPLETE CODE WITH ALL THE FUNCTIONS, in every single response."""

    coder = autogen.AssistantAgent(
        name="coder",
        is_termination_msg=termination_msg,
        system_message=coder_system_message,
        llm_config={
        "timeout": 5000,
        "seed": 42,
        "config_list": config_list,
        "temperature": 0,
    }
    )

    user_proxy.register_function(
        function_map={
            "web_scraping": web_scraping
        }
    )

    # ------------------ start conversation ------------------ #
    user_proxy.initiate_chat(coder, message=user_system_message)

    print("USER PROXY CHAT MESSAGEs:", str(user_proxy.chat_messages))
    return str(user_proxy.chat_messages)
