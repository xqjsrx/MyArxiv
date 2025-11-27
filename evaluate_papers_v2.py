import os
import json
from openai import OpenAI

# 填写API的密钥
API_KEY = os.getenv("API_KEY")

# 自定义的提示模板
PROMPT_TEMPLATE = """
我是一名人工智能方向的研究生，核心研究领域是 **文档图像理解（DIU / DocVQA）**。
我的目标是利用 **VLM (Multimodal LLM)** 技术解决文档理解中的核心痛点（如OCR幻觉、密集文本、复杂排版、长文档推理）。

请担任一名**挑剔的审稿人**，帮我筛选论文。
**原则：不拘泥于特定技术路线（如必须是Agent或必须是Intervention），只要能提升DIU性能的底层方法都值得关注；但坚决抵制无营养的“平行应用”。**

### 🛑 负面清单（直接打0-3分）
**只要命中以下任意一点，无需留情，直接低分：**
1.  **平行下游应用（Wrapper/Application）**：
    *   例如：“用LLM进行金融报表分析”、“基于RAG的法律文书助手”、“医疗病历结构化”。
    *   **理由**：这些只是把现有技术用在特定数据上，没有方法论创新。我只要提出技术源头的论文。
2.  **无关领域**：
    *   视频理解/生成、纯图像生成/修复、具身智能/机器人、自动驾驶、3D视觉。
    *   纯NLP的安全/对齐（Safety/Jailbreak）/政治正确，除非涉及“视觉幻觉”消除。
3.  **小语种**：非中英的特定语言数据集或模型。

### ✅ 关注领域与评分标准

#### 1. DIU 本题 (High Priority) -> [7-10分]
*   **任务**：DocVQA, Layout Analysis, Table Recognition, VIE/KIE, OCR-free End-to-End。
*   **趋势**：
    *   **DeepSeek-OCR 路线**：**Visual Token Compression (视觉压缩)**、Visual Representation Learning。
    *   **VLM for Doc**：专为文档设计的VLM架构、训练策略或高质量数据集。
*   *注：DIU领域内即使是传统方法或效率优化，也请保留（给及格分），因为圈子小，不宜漏掉。*

#### 2. 关联领域的“军火库” (Tools & Methodology) -> [6-9分]
**筛选标准：这篇上游论文提出的方法，能否被迁移来解决DIU的痛点？**
*   **痛点包括**：OCR幻觉（Hallucination）、细粒度定位（Grounding）、高分辨率处理、复杂逻辑推理。
*   **有价值的工具**：
    *   **Inference Scaling / Test-time Compute**：CoT、Search、Verification机制的**源头工作**。
    *   **VLM Architecture**：能显著提升High-Res输入处理能力或多模态对齐能力的架构改进。
    *   **Agent / Workflow**：能解决长文档阅读、多步信息检索过程中迷失问题的**Agent架构设计**（而非某个垂类Agent应用）。
    *   **Intervention / Steering**：推理阶段的干预或引导技术（作为一种可能的工具）。

### ❌ 这是一个发表信息提取任务
*   **Publication字段**：**仅**允许从 `comment` 字段提取！
*   **严禁**将 `category`（如 "cs.CV", "Computer Vision and Pattern Recognition"）当作发表信息。
*   如果 `comment` 为空或未提及会议/期刊，必须返回 "N/A"。

### 📝 打分参考 (0-10)
*   **9-10 (Must Read)**：DIU的SOTA工作；或者上游领域具有**范式转移（Paradigm Shift）**意义的底层创新（如Visual Token Compression的开山之作，或推理Scaling的新原理）。
*   **7-8 (Strong)**：扎实的DIU工作；或者能明显看到对DIU有迁移价值的上游新方法（如一种新的VQA去幻觉策略）。
*   **4-6 (Weak)**：DIU领域的常规灌水；或者虽是上游热点但迁移到文档极其困难的工作。
*   **0-3 (Reject)**：平行应用、无关领域、小语种。

### ✅ 任务指令
请根据以上标准评估。
1.  **Score**: 整数。
2.  **Title_zh**: 翻译标题。
3.  **Reason**: **中文**。
    *   **DIU论文**：简述其针对什么文档任务做了什么改进。
    *   **上游论文**：**核心必须解释该方法如何迁移到DIU领域**（例如：“该VLM分辨率处理方法可直接用于提升文档细粒度识别”）。
4.  **Summary**: 中文总结。
5.  **Keywords**: 3-5个关键词。
6.  **Publication**: 提取会议/期刊。

论文信息：
title：{title}
authors：{authors}
abstract：{abstract}
comment：{comment}
category：{category}

回复请用json格式，必须只返回json，不要返回其他内容：
"""

# JSON 响应模板
JSON_RESPONSE_TEMPLATE = """
{
  "score": x,
  "title_zh": "中文标题",
  "reason": "xxx",
  "summary": "xxx",
  "keywords": ["word1", "word2"],
  "publication": "xxx"
}
"""

def call_qwen_api(prompt):
    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-flash", 
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ]
        )
        print(completion)
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

def clean_json_response(response):
    start_index = response.find("{")
    end_index = response.rfind("}") + 1
    if start_index != -1 and end_index != -1:
        return response[start_index:end_index]
    return None

def evaluate_papers(input_file, output_file):
    with open(input_file, 'r') as f:
        papers = json.load(f)

    print(f"正在根据内容评估 {len(papers)} 篇论文...")

    for paper in papers:
        prompt = PROMPT_TEMPLATE.format(
            title=paper['title'],
            authors=', '.join(paper['authors']) if isinstance(paper['authors'], list) else paper['authors'],
            abstract=paper['abstract'],
            comment=paper.get('comment', ''),
            category=paper['category'],
        ) + JSON_RESPONSE_TEMPLATE
        
        # print(f"Evaluating: {paper['title']}")
        res = call_qwen_api(prompt)
        
        if res:
            cleaned_res = clean_json_response(res)
            if cleaned_res:
                try:
                    response = json.loads(cleaned_res)
                    paper['score'] = response.get('score', 0)
                    paper['reason'] = response.get('reason', 'N/A')
                    paper['summary'] = response.get('summary', 'N/A')
                    paper['keywords'] = response.get('keywords', [])
                    paper['title_zh'] = response.get('title_zh', '')
                    paper['publication'] = response.get('publication', 'N/A')
                except json.JSONDecodeError:
                    print(f"JSON解析失败: {cleaned_res}")
            else:
                print("未找到JSON")
        else:
            print("API调用失败")

    with open(output_file, 'w') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    evaluate_papers("target/latest_papers.json", "target/evaluated_papers.json")
