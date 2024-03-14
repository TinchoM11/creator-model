from utils.crawler import crawl_page

async def get_links_from_url(url):
    links = []
    print(url)
    result = await crawl_page(str(url))
    list_of_links = result["links"]
    content_file_path = result["content_file_path"]
    # should join list of links with links
    links = links + list_of_links
    
    print("LINKS:", links)
    return {"links": links, "content_file_path": content_file_path}
