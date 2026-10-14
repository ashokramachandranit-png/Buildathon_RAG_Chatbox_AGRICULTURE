import os
import re
import warnings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from playwright.sync_api import sync_playwright

warnings.filterwarnings("ignore")

# Targeted URLs focusing specifically on the Top 5 TN Agri Schemes & Subsidies
TARGET_URLS = [
    # Micro Irrigation / Drop by Drop Water Management
    "https://aed.tn.gov.in/en/schemes/water-management/electric-motor/",
    # Individual Subsidies & Farm Mechanization
    "https://aed.tn.gov.in/en/individual-based-subsidy-schemes/",
    "https://agritech.tnau.ac.in/agricultural_engineering/agriengg_govt_schemes.html",
    # TNAU Paddy, Seed Production & Expert Systems
    "https://agritech.tnau.ac.in/expert_system/paddy/Schemes.html",
    # Special Welfare & Skill Development Schemes
    "https://aed.tn.gov.in/en/schemes/special-schemes/skilldevelopment/",
    # Unified Farmer Portals
    "https://grains.tn.gov.in/",
    "https://pmfby.gov.in/"
]


def clean_text_content(text: str) -> str:
    """Removes web footers, YouTube subscription noise, and repeating social links."""
    text = re.sub(r"☞.*?(subscribe|channel|video).*?☜", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"(subscribe to our youtube channel|follow us on|all rights reserved|more videos).*?",
        "",
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def scrape_tn_agri_schemes(urls: list[str] = TARGET_URLS) -> list[Document]:
    """Scrapes portal index pages and scheme sub-links."""
    documents = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for base_url in urls:
            print(f"Scraping portal URL: {base_url}")
            try:
                page.goto(base_url, timeout=60000)
                main_content = page.inner_text("body")
                if main_content and len(main_content.strip()) > 100:
                    documents.append(
                        Document(
                            page_content=main_content,
                            metadata={"source": base_url, "type": "index_page"},
                        )
                    )
            except Exception as e:
                print(f"Warning: Could not crawl {base_url} ({e})")

        browser.close()
    return documents


def get_processed_chunks(urls: list[str] = TARGET_URLS) -> list[Document]:
    """Scrapes web content, cleans boilerplate, and splits into chunks."""
    docs = scrape_tn_agri_schemes(urls)
    print(f"Total raw documents collected: {len(docs)}")

    cleaned_docs = []
    for doc in docs:
        cleaned_content = clean_text_content(doc.page_content)
        if len(cleaned_content) > 100:
            doc.page_content = cleaned_content
            cleaned_docs.append(doc)

    print(f"Documents remaining after cleaning: {len(cleaned_docs)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(cleaned_docs)
    print(f"Total processed chunks created: {len(chunks)}")
    return chunks


if __name__ == "__main__":
    chunks = get_processed_chunks()
    print(f"Successfully generated {len(chunks)} clean text chunks.")