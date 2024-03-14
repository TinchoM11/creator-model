import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from config import config_list, chroma_client


def termination_msg(x): return isinstance(
    x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def generate_code_for_bridge(result_from_links, url, chain_id: str, rpc: str):

    links = result_from_links["links"]
    content_file_path = result_from_links["content_file_path"]

    # Start chatting with boss as this is the user proxy agent after user_proxy
    llm_config = {
        "timeout": 1000,
        "seed": 42,
        "config_list": config_list,
        "temperature": 0,
    }

    # create a rag agent for the links
    rag_agent = RetrieveUserProxyAgent(
        name="Boss_Assistant",
        is_termination_msg=termination_msg,
        system_message="""You are an assistant with extra content retrieval power for integrating bridge functionality for a blockchain. 
        Your role is to provide relevant information and guidance to the other agents to ensure they can implement the bridge correctly based on the documentation provided in {url}. 
        If an agent asks for help or clarification, provide them with the necessary information from the documentation.
        You know exactly the whole process of integrating a bridge for a blockchain, like quoting, executing, retreving status, and you must ensure that every step is implemented correctly.
        Reply 'TERMINATE' when the code for the bridge has been successfully generated and reviewed.""",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        retrieve_config={
            "task": "code",
                    "docs_path": content_file_path,
                    "chunk_token_size": 1000,
                    "model": config_list[0]["model"],
                    "collection_name": "groupchat",
                    "client": chroma_client,
                    "embedding_model": "all-mpnet-base-v2",
                    "get_or_create": True,
        },
        # we don't want to execute code in this case.
        code_execution_config=False
    )

    pm = autogen.AssistantAgent(
        name="Product_Manager",
        is_termination_msg=termination_msg,
        system_message="""
        You are an Product Manager specialized on Blockchain integrations, with a lot of knowledge for integrating bridging functionality for a blockchain. 
        Your role is to provide relevant information and guidance to the other agents to ensure they can implement the bridging functionality correctly for chain id {chain_id} with rpc {rpc} based on the documentation provided in {url}. 
        Your main task is to provide to Senior_Typescript_Engineer a plan to incorporate bridging functionality for the specified blockchain.
        If the Senior_Typescript_Engineer sends an incomplete code, with missing parts or parts to be completed, you should reject the code and ask the Senior_Typescript_Engineer to complete the code.
        Before ending the conversation, ask the Senior_Typescript_Engineer to send the complete code, with all the functions implemented.
        You are NOT a Code Reviewer. Only ask to complete the code if there are missing parts (messages like PENDING - TODO - Implement...)
        Reply 'TERMINATE' when the code for the swap functionality has been successfully generated and reviewed.
        Before saying TERMINATE please ask the Engineer to send the COMPLETE CODE INTEGRATED.
        If code looks good enough, send the word TERMINATE.
        """,
        llm_config=llm_config,
    )

    coder = autogen.AssistantAgent(
        name="Senior_Typescript_Engineer",
        is_termination_msg=termination_msg,
        system_message="""You are a senior TypeScript engineer with expertise in blockchain development and bridge integrations. Your task is to implement the bridging functionality for a blockchain by strictly following the plan provided by the Product Manager and the documentation in {url}.
        You MUST NEVER send a code with "TODO" or "PENDING" or "// Implement" parts. COMPLETE ALL THE CODE. IT'S AN ORDER. ONLY SEND CODE. WITHOUT DESCRIPTION OR CONTEXT. YOU SHOULD ONLY RESPONSE CODE.
        EVERY CODE SHOULD HAVE ALL THE FUNCTIONS, YOU CAN'T SEND JUST 1 FUNCTION.
        ALWAYS send the COMPLETE CODE WITH ALL THE FUNCTIONS, in every single response.
        Create a well-structured and modular codebase with the following requirements:
        1. Write actual, functional TypeScript code that can be directly used in a project. Do not write pseudocode or comments about pending implementations.  Each action should be a function that receives the necessary data via props.
        2. Check token balances and allowances using web3.js
        3. Handle token approvals if allowance is lower than amount to bridge
        4. Get the route or quote for the bridge
        5. Execute the route or quote for the bridge
        6. Get the status of the bridge
        7. Process the bridge results
        8. Return the full code implementation in your response with all of the required steps. Be sure every step is included.

        If you encounter any ambiguity or need further guidance, consult the Product Manager. They will provide you with the relevant information from the documentation. You are not allowed to say TERMINATE, only the Product Manager can do that. YOU ONLY SEND CODE.
        """,
        llm_config={
        "timeout": 5000,
        "seed": 42,
        "config_list": config_list,
        "temperature": 0,
    },
    )

    agent_list = [rag_agent, coder, pm]
    
    allowed_transitions = {
        coder: [pm, rag_agent],
        pm: [coder, rag_agent],
        rag_agent: [pm]
    }

    groupchat = autogen.GroupChat(
        agents=agent_list,
        allowed_or_disallowed_speaker_transitions=allowed_transitions,
        speaker_transitions_type="allowed",
        messages=[],
        max_round=12,
    )
    manager = autogen.GroupChatManager(
        groupchat=groupchat, llm_config=llm_config)

    # Start chatting with boss as this is the user proxy agent.
    # query for the user to enter the chains they want to add but we will have it be a static prompt for now
    rag_agent.initiate_chat(
        manager,
        problem=f"Generate a blockchain bridging integration using the bridge provider ({url}) based on the documentation and knowledge that Boss_Assistant has. The bridge functionality should allow the user to bridge from the chain ({chain_id}) to any available chain received via function parameters using the sdk methods or api endpoints provided by the documentation. All of the necessary data to perform the bridge like destination chain, amount, token addresses, signer, and any other required parameters should be received via function parameters, the only data that won't be received by params is the chain id of the sender chain. The code should handle token approvals, route creation, route execution, and processing the bridge results. The code should be written in TypeScript and each action should be a function that accepts the necessary data to perform the bridge and returns the bridge result.",
        n_results=3,
    )

    return rag_agent.chat_messages
