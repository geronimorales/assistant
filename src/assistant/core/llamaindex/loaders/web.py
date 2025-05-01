from typing import List, Optional

from pydantic import BaseModel, Field


class CrawlUrl(BaseModel):
    base_url: str
    prefix: str
    max_depth: int = Field(default=1, ge=0)


class WebLoaderConfig(BaseModel):
    driver_arguments: Optional[List[str]] = Field(default_factory=list)
    urls: List[CrawlUrl]


class WebPageLoaderConfig(BaseModel):
    urls: List[str]


def get_web_documents(config: WebLoaderConfig):
    from llama_index.readers.web import WholeSiteReader
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    driver_arguments = config.driver_arguments or []
    for arg in driver_arguments:
        options.add_argument(arg)

    docs = []
    for url in config.urls:
        scraper = WholeSiteReader(
            prefix=url.prefix,
            max_depth=url.max_depth,
            driver=webdriver.Chrome(options=options),
        )
        docs.extend(scraper.load_data(url.base_url))

    return docs


def get_web_page_documents(config: WebPageLoaderConfig):
    from llama_index.readers.web import SimpleWebPageReader

    docs = []
    scraper = SimpleWebPageReader(html_to_text=True, metadata_fn=set_metadata)
    docs = scraper.load_data(config.urls)

    print(f"Loaded {len(docs)} documents from web pages.")
    for doc in docs:
        print(f"Document: {doc}")
    return docs


def set_metadata(str):
    return {"url": str}
