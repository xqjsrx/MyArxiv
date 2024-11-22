import json
import re
import os
from bs4 import BeautifulSoup

def clean_html(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text().strip()

def remove_symbols_and_newlines(text):
    # 使用正则表达式移除标题前的符号和所有换行符
    text = re.sub(r'^[\u2600-\u26ff\u2700-\u27bf\s]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_paper_info(html_file, output_file):
    print(f"Current working directory: {os.getcwd()}")
    print(f"Reading HTML file from: {html_file}")
    
    with open(html_file, "r") as f:
        content = f.read()

    pattern = re.compile(r'<article>\s*<details class="article-expander"(?: open="")?>\s*<summary class="article-expander-title">(.*?)</summary>\s*<div class="article-authors">(.*?)</div>\s*<div class="article-summary-box-inner">\s*<span>(.*?)</span>\s*</div>', re.DOTALL)
    papers = []

    for title, authors, abstract in pattern.findall(content):
        title = clean_html(title)
        title = remove_symbols_and_newlines(title)
        authors = clean_html(authors)
        authors = remove_symbols_and_newlines(authors)
        abstract = clean_html(abstract)
        abstract = remove_symbols_and_newlines(abstract)
        papers.append({"title": title, "authors": authors, "abstract": abstract})

    print(f"Writing papers to: {output_file}")
    with open(output_file, "w") as f:
        json.dump(papers, f, indent=2)

if __name__ == "__main__":
    extract_paper_info("target/index.html", "target/papers.json")
