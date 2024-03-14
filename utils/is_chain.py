from utils.check_chain_list import get_chain_list
def is_chain(item_name):
    chain_list = get_chain_list(item_name)  # Assuming there is a function to get the list from the website
    if item_name in chain_list:
        return True
    else:
        return False
    

