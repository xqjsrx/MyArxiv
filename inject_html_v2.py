import json
import re
from bs4 import BeautifulSoup

# 读取文件
with open("target/evaluated_papers.json", 'r') as f:
    evaluated_papers = json.load(f)

with open("target/index.html", 'r') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 过滤与排序
scored_papers = [p for p in evaluated_papers if 'score' in p and isinstance(p['score'], int)]
scored_papers.sort(key=lambda x: x['score'], reverse=True)

# 辅助函数：创建统一格式的 'Label + Content' 行
def create_row_with_label(soup, label_text, content_text):
    if not content_text or content_text == "N/A":
        return None
        
    div = soup.new_tag('div', **{'class': 'article-summary-box-inner', 'style': 'margin-top: 6px;'})
    
    # Label: 使用原生 class="chip"
    label = soup.new_tag('span', **{'class': 'chip'})
    label.string = label_text
    div.append(label)
    
    # Content: 不加 style，跟随主题
    content = soup.new_tag('span', **{'style': 'margin-left: 8px;'})
    content.string = str(content_text)
    div.append(content)
    
    return div

# ----------------- 构建页面 -----------------

if scored_papers:
    # 容器边框颜色最好还是指定一下，不然可能看不出来，这里用了 var(--nord08) 即原本的主题色
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 20px; border: 2px solid var(--nord08);'})
    
    # 头部：颜色跟随 .date 类
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'padding-bottom: 15px; border-bottom: 1px solid var(--nord04); margin-bottom: 15px;'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    for paper in scored_papers:
        article = soup.new_tag('article', **{'style': 'margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px dashed var(--nord03);'})
        # 默认展开
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true'})
        
        # === 第1行：Score | Title | Publication ===
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'display: flex; align-items: baseline; flex-wrap: wrap;'})
        
        # Score (使用 chip 样式，手动加个背景色区分，或者直接用默认 chip)
        # 为了突出分数，这里保留一点点自定义背景，也可以删掉 style 变成默认 chip
        score_span = soup.new_tag('span', **{'class': 'chip', 'style': 'background: var(--nord0B); color: white; margin-right: 8px;'})
        score_span.string = str(paper['score'])
        summary_tag.append(score_span)
        
        # Title
        title_span = soup.new_tag('span', **{'style': 'font-size: 1.1em; margin-right: 10px; font-weight: bold;'})
        title_span.string = paper['title']
        summary_tag.append(title_span)
        
        # Publication (Extracted by AI)
        if paper.get('publication') and paper['publication'] != "N/A":
            # 使用默认 chip 样式
            pub_span = soup.new_tag('span', **{'class': 'chip'})
            pub_span.string = paper['publication']
            summary_tag.append(pub_span)
            
        details.append(summary_tag)

        # === 第2行：Links | Authors ===
        # 使用 article-authors 类，保持原生颜色
        meta_div = soup.new_tag('div', **{'class': 'article-authors', 'style': 'margin: 5px 0; display: flex; align-items: center;'})
        
        # Link Logic
        abs_link = paper['id']
        pdf_link = abs_link.replace('/abs/', '/pdf/')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)

        # Icons
        link_a = soup.new_tag('a', href=abs_link, target="_blank", **{'style': 'margin-right: 10px; text-decoration: none;'})
        link_i = soup.new_tag('i', **{'class': 'ri-links-line'}) # 原生图标
        link_a.append(link_i)
        meta_div.append(link_a)
        
        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'style': 'margin-right: 15px; text-decoration: none;'})
        pdf_i = soup.new_tag('i', **{'class': 'ri-file-pdf-line'}) # 使用 RemixIcon 的 PDF 图标
        pdf_a.append(pdf_i)
        meta_div.append(pdf_a)

        # Authors (不加 style，继承 article-authors 的颜色)
        authors_text = soup.new_tag('span')
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        meta_div.append(authors_text)
        
        details.append(meta_div)

        # === 第3行：Title Translation ===
        if paper.get('title_zh'):
            trans_row = create_row_with_label(soup, "Title CN", paper['title_zh'])
            if trans_row: details.append(trans_row)

        # === 第4行：AI Keywords ===
        keywords = paper.get('keywords', [])
        if keywords:
            if isinstance(keywords, list):
                keywords_str = " · ".join(keywords)
            else:
                keywords_str = keywords
            kw_row = create_row_with_label(soup, "AI Keywords", keywords_str)
            if kw_row: details.append(kw_row)

        # === 第5行：AI Summary ===
        sum_row = create_row_with_label(soup, "AI Summary", paper.get('summary', ''))
        if sum_row: details.append(sum_row)

        # === 第6行：AI Reason ===
        reason_row = create_row_with_label(soup, "AI Reason", paper.get('reason', ''))
        if reason_row: details.append(reason_row)

        # === 第7行：Original Abstract ===
        abs_row = create_row_with_label(soup, "Original Abstract", paper.get('abstract', ''))
        if abs_row: details.append(abs_row)

        # === 第8行：Raw Comment ===
        if paper.get('comment'):
            com_row = create_row_with_label(soup, "Raw Comment", paper['comment'])
            if com_row: details.append(com_row)

        # === 第9行：Categories ===
        cat_row = create_row_with_label(soup, "Categories", paper.get('category', ''))
        if cat_row: details.append(cat_row)

        article.append(details)
        top_section.append(article)

    # 插入 Header
    header_container = soup.find('section', class_='header-container')
    if header_container:
        header_container.insert_after(top_section)
    else:
        soup.body.insert(0, top_section)

# 写回
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print("HTML injection complete.")
