from playwright.async_api import async_playwright
from urllib.parse import urlparse

async def crawl_page(url, max_pages=10):
    urls = []  # List to store URLs
    visited_pages = 0  # Counter for visited pages

    # Parse the base domain from the initial URL
    base_domain = urlparse(url).netloc
    print("Base domain:", base_domain)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        file_path = f"./content.txt"
        # Queue of URLs to visit
        url_queue = [url]

        while url_queue and visited_pages < max_pages:
            current_url = url_queue.pop(0)
            print("Visiting", current_url)
            await page.goto(str(current_url))

            

            visited_pages += 1
            
            # Extract all links on the page
            link_elements = await page.query_selector_all("a")
            page_content = await page.locator("body").inner_text()
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(page_content)
            for link_element in link_elements:
                link_url = await link_element.get_attribute("href")
                # print("1 Link URL:", link_url)
                if link_url.startswith("#"):
                    # Skip anchor links
                    # print("2 Skipping anchor link")
                    continue
                if link_url.startswith("/"):
                    # Create full URL from relative path
                    full_url = "https://" + base_domain + link_url
                    urls.append(full_url)
                    url_queue.append(full_url)
                    print(f"1 Added {full_url} to the queue")
                elif base_domain in link_url:
                    urls.append(link_url)
                    url_queue.append(link_url)
                    print(f"2 Added {link_url} to the queue")
                # elif link_url and urlparse(link_url).netloc != base_domain:
                #     print(f"4 No links found for {url} with {link_url}")
            
        file.close()   

        await browser.close()


    return {"links": list(set(urls)), "content_file_path": file_path}


# async def crawl_page(url, max_pages=50):
#     urls = []  # List to store URLs
#     visited_pages = 0  # Counter for visited pages
#     base_url = url.split("/")[2]

#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()

#         # Queue of URLs to visit
#         url_queue = [url]

#         while url_queue and visited_pages < max_pages:
#             current_url = url_queue.pop(0)
#             print("Visiting", current_url)
#             await page.goto(str(current_url))
#             visited_pages += 1
#             # Extract all links on the page
#             link_elements = await page.query_selector_all("a")
#             for link_element in link_elements:
#                 link_url = await link_element.get_attribute("href")
#                 if link_url and link_url not in urls and re.match(r'https?://[^\s\n"\'<>]+', link_url) :
#                     urls.append(link_url)
#                     url_queue.append(link_url)  # Add new URL to the queue

#         await browser.close()

#     return urls
