import autogen
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from config import config_list, chroma_client

def termination_msg(x): return isinstance(
    x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

def generate_code_for_dex(result_from_links, url, rpc: str, chain_id: str):
    links = result_from_links["links"]
    content_file_path = result_from_links["content_file_path"]

    # Start chatting with boss as this is the user proxy agent after user_proxy
    llm_config = {
        "timeout": 5000,
        "seed": 42,
        "config_list": config_list,
        "temperature": 0,
    }

    # create a rag agent for the links
    rag_agent = RetrieveUserProxyAgent(
        name="Boss_Assistant",
        is_termination_msg=termination_msg,
        system_message=f"""You are an assistant with extra content retrieval power for integrating decentralized exchange swap functionality for a blockchain. 
               Your role is to provide relevant information and guidance to the other agents to ensure they can implement the swap functionality correctly based on the documentation provided in {url}. 
               If an agent asks for help or clarification, provide them with the necessary information from the documentation.
               If the documentation provided in {url} involves using API Calls, provide the necessary endpoints and parameters to the agents.
                If the documentation provided in {url} involves using SDKs, provide the necessary functions and parameters to the agents.
                If the documentation provided in {url} involves making Contract Calls, provide the contracta address and necessary functions to be included ABI of the contract.
               Reply 'TERMINATE' when the code for the swap functionality has been successfully generated and reviewed.""",
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
        code_execution_config=False,
    )

    pm = autogen.AssistantAgent(
        name="Product_Manager",
        is_termination_msg=termination_msg,
        system_message=f"""You are an Product Manager specialized on Blockchain integrations, with a lot of knowldege for integrating decentralized exchange swap functionality for a blockchain. 
       Your role is to provide relevant information and guidance to the other agents to ensure they can implement the swap functionality correctly based on the documentation provided in {url} and the rpc url {rpc}. 
       Your main task is to provide to Senior_Typescript_Engineer a plan to incorporate swap functionality for the specified blockchain.
       If the Senior_Typescript_Engineer sends an incomplete code, with missing parts or parts to be completed, you should reject the code and ask the Senior_Typescript_Engineer to complete the code.
       Before ending the conversation, ask the Senior_Typescript_Engineer to send the complete code, with all the functions implemented.
       You are NOT a Code Reviewer. Only ask to complete the code if there are missing parts (messages like PENDING - TODO - Implement...)
       Reply 'TERMINATE' when the code for the swap functionality has been successfully generated and reviewed.
       Before saying TERMINATE please ask the Engineer to send the COMPLETE CODE INTEGRATED.
       If code looks good enough, send the word TERMINATE.""",
        llm_config=llm_config,
    )

    coder = autogen.AssistantAgent(
        name="Senior_Typescript_Engineer",
        is_termination_msg=termination_msg,
        system_message=f"""You are a senior TypeScript engineer with expertise in blockchain development and decentralized exchange integrations. 
        You MUST NEVER send a code with "TODO" or "PENDING" or "// Implement" parts. COMPLETE ALL THE CODE. IT'S AN ORDER.
        Your main task is to implement the swap functionality for the specified blockchain by strictly following the plan provided by the Product Manager and the documentation in {url} and the rpc url {rpc}.
        Manage every number as BigNumbers. Use ethers.js library if needed for this.
        ONLY SEND CODE. WITHOUT DESCRIPTION OR CONTEXT. YOU SHOULD ONLY RESPONSE CODE.
        EVERY CODE SHOULD HAVE ALL THE FUNCTIONS, YOU CAN'T SEND JUST 1 FUNCTION.
        ALWAYS send the COMPLETE CODE WITH ALL THE FUNCTIONS, in every single response.
        FUNCTIONS TO INCLUDE:
        1. Check token balances and allowances using web3.js
        2. Handle token approvals if allowance is lower than amount to swap
        3. Construct the swap QUOTE request payload according to the decentralized exchange's API or SDK
        4. Execute the swap QUOTE request to the decentralized exchange (with this I mean the function that executes the swap)
        5. Process the swap response getting the transaction receipt from the transaction hash.
        6. Return the swap transaction details (Transaction Receipt)
        7. Testing and Documentation is NOT required.
        8. Should be able to swap from Native Tokens to ERC20 Tokens and vice versa, and between ERC20 Tokens.
        9. All the swap flow should be done in a single function called executeSwapTransaction, calling inside the necessary sub-functions.
        You are not allowed to say TERMINATE, only the Product Manager can do that. YOY ONLY SEND CODE""",
        llm_config=llm_config,
    )

    # reviewer = autogen.AssistantAgent(
    #     name="Code_Reviewer",
    #     is_termination_msg=termination_msg,
    #     system_message=f"""You are a code reviewer. Thoroughly review the code provided by the Senior_Typescript_Engineer to ensure it meets the highest quality standards and correctly implements the swap functionality as described in the documentation ({url}).
    # If you see any part with 'TODO' or 'PENDING' or 'IMPLEMENT' or comments like '// Implement.....' just reject the code and ask the Senior_Typescript_Engineer to complete the code.
    # Check always that the code is complete, and not just parts of it.
    # If no code is provided to you, ask for the code always. Don't do anything if you don't have any code.
    # If code looks good enough, send the word TERMINATE.
    # Check for proper structure, modularity and error handling. No TESTING or DOCUMENTATION is required. Don't ask for this.""",
    #     llm_config=llm_config,
    # )

    agent_list = [rag_agent, coder, pm]

    allowed_transitions = {
        # reviewer: [coder],
        coder: [pm, rag_agent],
        pm: [coder, rag_agent],
        rag_agent: [pm]
    }

    groupchat = autogen.GroupChat(
        agents=agent_list,
        allowed_or_disallowed_speaker_transitions=allowed_transitions,
        speaker_transitions_type="allowed",
        messages=[],
        max_round=20,
    )
    manager = autogen.GroupChatManager(
        groupchat=groupchat, llm_config=llm_config)

    # Start chatting with boss as this is the user proxy agent.
    # query for the user to enter the chains they want to add but we will have it be a static prompt for now
    rag_agent.initiate_chat(
        manager,
        problem=f"Estimated Product Manager, we need to generate a blockchain swap integration for the decentralized exchange {url} based on the documentation and knowledge that Boss_Assistant has. The swap functionality should allow users to swap tokens on the specified blockchain using the provided RPC URL ({rpc}). The code should handle token approvals, make swap requests to the decentralized exchange, execute the swap request, and process the swap results. Ensure that the necessary data for the swap, such as token addresses, amounts, and gas settings, are received via function parameters. Please coordinate with Senior_Typescript_Engineer and provide him a plan to incorporate swap functionality for the specified blockchain.",
        n_results=3,
    )

    return rag_agent.chat_messages
