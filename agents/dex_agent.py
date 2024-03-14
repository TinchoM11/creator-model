# This is a research agent that is designed to research how we would add a blockchain to the interoperability layer.

from autogen import UserProxyAgent
import autogen
from utils.web_search import web_search
from utils.defi_llama import get_all_dexes
from utils.web_scrape import web_scraping
from config import config_list

termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def start_bot(prompt):
    user_system_message ="""Initiate research to get the javascript developer documentation for a DEX SDK for a particular blockchain. 
    Leverage your ability to run code and execute functions. If any function fails use web_search as a fallback. 
    Make sure to repeat the links back before terminating.
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
                    "description": "Search the web for developer documentation links for a dexes",
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
                    "name": "get_all_dexes",
                    "description": "Get a list of dexes for a specific blockchain",
                    "parameters": {
                        "type": "object",
                        "properties": {
                        "blockchain": {
                            "type": "string",
                            "description": "The blockchain"
                        }
                        },
                        "required": [
                        "blockchain"
                        ]
                        }
                    }
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
            "get_all_dexes": get_all_dexes,
        }
    )


    # ------------------ start conversation ------------------ #
    user_proxy.initiate_chat(researcher, message=prompt)

    print("LAST USER PROXY CHAT MESSAGE:", str(user_proxy.last_message(researcher)))
    return str(user_proxy.last_message(researcher))
    # return user_proxy.chat_messages


def get_dex_agent_response(message):
    prompt = message
    print(f"Received prompt: {prompt}")
    chat_history = start_bot(str(prompt))
    return chat_history

    
