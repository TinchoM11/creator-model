import re

def extract_urls(text):
    # Regular expression to find URLs
    url_pattern = r'https?://[^\s"\'<>]+(?=/|\s|[,.?!;:\'")])'
    # Find all matches in the text
    urls = re.findall(url_pattern, text)

    # clean up the urls after the last slash and before the ) in 'https://docs.uniswap.org/).\n\nSo,'
    urls = [url.split(")")[0] for url in urls]
    return urls