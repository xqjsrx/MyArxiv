import json
import re
import os
from bs4 import BeautifulSoup

def clean_html(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text().strip()

def extract_paper_info(html_file, output_file):
    print(f"Current working directory: {os.getcwd()}")
    print(f"Reading HTML file from: {html_file}")
    
    with open(html_file, "r") as f:
        content = f.read()

    pattern = re.compile(r'<article>\s*<details class="article-expander"(?: open="")?>\s*<summary class="article-expander-title">(.*?)</summary>\s*<div class="article-authors">(.*?)</div>\s*<div class="article-summary-box-inner">\s*<span>(.*?)</span>\s*</div>', re.DOTALL)
    papers = []

    for title, authors, abstract in pattern.findall(content):
        title = clean_html(title)
        authors = clean_html(authors)
        abstract = clean_html(abstract)
        papers.append({"title": title, "authors": authors, "abstract": abstract})

    print(f"Writing papers to: {output_file}")
    with open(output_file, "w") as f:
        json.dump(papers, f, indent=2)

if __name__ == "__main__":
    extract_paper_info("target/index.html", "target/papers.json")
