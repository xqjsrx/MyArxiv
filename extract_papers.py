import json
import re
import os

def extract_paper_info(html_file, output_file):
    print(f"Current working directory: {os.getcwd()}")
    print(f"Reading HTML file from: {html_file}")
    
    with open(html_file, "r") as f:
        content = f.read()

    pattern = re.compile(r'<article>\s*<details class="article-expander"(?: open="")?>\s*<summary class="article-expander-title">(.*?)</summary>\s*<div class="article-authors">(.*?)</div>\s*<div class="article-summary-box-inner">\s*<span>(.*?)</span>\s*</div>', re.DOTALL)
    papers = []

    for title, authors, abstract in pattern.findall(content):
        title = title.strip()
        authors = re.sub(r"<a[^>]*>", "", authors).strip()  # 移除作者链接标签
        abstract = abstract.strip()
        papers.append({"title": title, "authors": authors, "abstract": abstract})

    print(f"Writing papers to: {output_file}")
    print(papers)
    with open(output_file, "w") as f:
        json.dump(papers, f, indent=2)

if __name__ == "__main__":
    extract_paper_info("target/index.html", "target/papers.json")
