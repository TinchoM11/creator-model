# This is a research agent that is designed to research how we would add a blockchain to the interoperability layer.

from autogen import UserProxyAgent
import autogen
from utils.web_search import web_search
from utils.defi_llama import get_all_bridges
from utils.web_scrape import web_scraping


termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def start_bot(prompt):
    user_system_message ="""Initiate research to get the javascript developer SDK documentation to integrate a bridge for the neccesary blockchain.
        Leverage your ability to execute functions to find developer documentation for the bridge the user is wanting to add and how we are supposed to add it.
        To add a bridge, you will need to find the developer documentation for the bridge's javascript sdk.
        Make sure you find the docs not only for getting a bridge quote, but also for executing it.
        If any function fails use web_search as a fallback. Make sure to repeat the links back before terminating. 
        Reply TERMINATE when we have a developer documentation links for what the user is wanting to add. """

    # Create user proxy agent
    user_proxy = UserProxyAgent(name="user_proxy",
        is_termination_msg=termination_msg,
        human_input_mode="NEVER",
        system_message=user_system_message,
        code_execution_config={"work_dir": "web", "use_docker": False},
    )

    llm_config = {
            "timeout": 1000,
            "seed": 43,
            "config_list": config_list,
            "temperature": 0,
            "functions": [
                    {
                    "name": "web_search",
                    "description": "Search the web for developer documentation links for a bridge",
                        "parameters": {
                            "type": "object",
                            "properties": {
                            "search_keyword": {
                                "type": "string",
                                "description": "A great search query to receive the correct developer documentation link."
                            }
                            },
                            "required": [
                            "search_keyword"
                            ]
                        }
                    },
                    {
                    "name": "web_scraping",
                    "description": "scrape website content based on url",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "url": {
                            "type": "string",
                            "description": "the url of the website you want to scrape from web_search or user input"
                        }
                        },
                        "required": [
                        "url"
                        ]
                        }
                    },
                    {
                    "name": "get_all_bridges",
                    "description": "Get a list of all of the bridges that are used with their chains listed in the returned object from this funciton. Can be used to filter to find a correct bridge and use this information to search for the 'bridge name' developer documentation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "blockchain": {
                            "type": "string",
                            "description": "The name of the blockchain the user is trying to add"
                        }
                        },
                        "required": [
                        "blockchain"
                        ]
                        }
                    },
                ]
        }

    researcher_system_message = """Do not code anything, just do research. Reply TERMINATE when we have all of the information we need."""

    researcher = autogen.AssistantAgent(
            name="researcher",
            is_termination_msg=termination_msg,
            system_message=researcher_system_message,
            llm_config=llm_config,
        )

    user_proxy.register_function(
        function_map={
            "web_scraping": web_scraping,
            "web_search": web_search,
            "get_all_bridges": get_all_bridges,
        }
    )


    # ------------------ start conversation ------------------ #
    user_proxy.initiate_chat(researcher, message=prompt)

    print("LAST USER PROXY CHAT MESSAGE:", str(user_proxy.last_message(researcher)))
    return str(user_proxy.last_message(researcher))
    # return user_proxy.chat_messages

def get_bridge_agent_response(message):
    prompt = message
    print(f"Received prompt: {prompt}")
    chat_history = start_bot(str(prompt))
    return chat_history

    
