import json
from bs4 import BeautifulSoup

# 读取经过AI打分的文件
with open("target/evaluated_papers.json", 'r') as f:
    evaluated_papers = json.load(f)

# 读取 HTML 文件
with open("target/index.html", 'r') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 1. 过滤并排序论文
# 只保留有评分的论文
scored_papers = [p for p in evaluated_papers if 'score' in p and isinstance(p['score'], int)]
# 按分数降序排列
scored_papers.sort(key=lambda x: x['score'], reverse=True)

# 2. 构建“本周精选”的 HTML 结构
# 我们尽量复用原本的 CSS 类 (day-container, article-expander 等) 保持样式一致

if scored_papers:
    # 创建外层容器
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 20px; border: 2px solid var(--nord08);'})
    
    # 标题栏
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'color: var(--nord0B); padding-bottom: 10px;'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    # 遍历排序后的论文，生成 HTML 卡片
    for paper in scored_papers:
        # 创建文章容器
        article = soup.new_tag('article')
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true'}) # 默认展开高分论文
        
        # --- Summary (标题行) ---
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title'})
        
        # 1. 分数 Chip
        score_span = soup.new_tag('span', **{'class': 'chip', 'style': 'background: var(--nord0B); color: white; font-weight: bold;'})
        score_span.string = str(paper['score'])
        summary_tag.append(score_span)
        summary_tag.append(" ") # 空格

        # 2. 标题文本
        title_span = soup.new_tag('span')
        # 这里为了简单没加原本的正则高亮，如果需要可以后续加上，或者直接用文本
        title_span.string = paper['title']
        summary_tag.append(title_span)
        
        # 3. 会议/Comment Chip (如果有)
        if paper.get('comment'):
            summary_tag.append(" ")
            conf_span = soup.new_tag('span', **{'class': 'chip'})
            conf_span.string = paper['comment']
            summary_tag.append(conf_span)

        details.append(summary_tag)

        # --- Content (内容详情) ---
        
        # 作者行
        authors_div = soup.new_tag('div', **{'class': 'article-authors'})
        
        # 链接图标
        link_a = soup.new_tag('a', href=paper['id'], target="_blank")
        icon_i = soup.new_tag('i', **{'class': 'ri-links-line'})
        link_a.append(icon_i)
        authors_div.append(link_a)
        authors_div.append(" ")

        # 作者列表
        authors_text = soup.new_tag('span')
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        authors_div.append(authors_text)
        details.append(authors_div)

        # AI 评价理由 (Reason)
        reason_div = soup.new_tag('div', **{'class': 'article-summary-box-inner', 'style': 'background-color: rgba(136, 192, 208, 0.1); padding: 10px; border-radius: 5px; margin: 5px 0;'})
        reason_label = soup.new_tag('span', **{'class': 'chip'})
        reason_label.string = "AI Reason"
        reason_content = soup.new_tag('span', **{'style': 'font-weight: 500; color: var(--nord0B);'})
        reason_content.string = paper.get('reason', '')
        reason_div.append(reason_label)
        reason_div.append(" ")
        reason_div.append(reason_content)
        details.append(reason_div)

        # AI 总结 (Summary)
        ai_summary_div = soup.new_tag('div', **{'class': 'article-summary-box-inner'})
        summary_label = soup.new_tag('span', **{'class': 'chip'})
        summary_label.string = "AI Summary"
        summary_content = soup.new_tag('span')
        summary_content.string = paper.get('summary', '')
        ai_summary_div.append(summary_label)
        ai_summary_div.append(" ")
        ai_summary_div.append(summary_content)
        details.append(ai_summary_div)
        
        # 原文摘要 (Abstract) - 默认折叠或放在最后
        abs_div = soup.new_tag('div', **{'class': 'article-summary-box-inner', 'style': 'color: var(--nord03); font-size: 0.9em;'})
        abs_label = soup.new_tag('span', **{'class': 'chip', 'style': 'background: var(--nord04); color: var(--nord00);'})
        abs_label.string = "Original Abstract"
        abs_content = soup.new_tag('span')
        abs_content.string = paper.get('abstract', '')
        abs_div.append(abs_label)
        abs_div.append(" ")
        abs_div.append(abs_content)
        details.append(abs_div)

        # 类别标签
        cat_div = soup.new_tag('div', **{'class': 'article-summary-box-inner'})
        cat_span = soup.new_tag('span', **{'class': 'chip'})
        cat_span.string = f"Categories: {paper.get('category', '')}"
        cat_div.append(cat_span)
        details.append(cat_div)

        article.append(details)
        top_section.append(article)

    # 3. 插入到页面顶部
    # 找到原来的 header-container
    header_container = soup.find('section', class_='header-container')
    if header_container:
        # 插入到 header 之后
        header_container.insert_after(top_section)
    else:
        # 如果找不到 header，插入到 body 的最前面
        soup.body.insert(0, top_section)

# 4. (可选) 如果你想移除下面每日列表中重复的卡片，可以在这里添加逻辑。
# 但保留每日列表作为全量数据的存档通常也是不错的选择。

# 写回文件
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print(f"Index.html updated. Inserted Weekly Top Picks with {len(scored_papers)} papers.")
