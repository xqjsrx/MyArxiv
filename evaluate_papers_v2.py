import os
import json
from openai import OpenAI

# 填写API的密钥
API_KEY = os.getenv("API_KEY")

# 自定义的提示模板
PROMPT_TEMPLATE = """
我是一名人工智能方向的研究生，专注于文档图像理解（Document Image Understanding, DIU）。
请扮演我的科研助手，严格根据我的研究兴趣对今天的Arxiv论文进行筛选、打分和总结。

### 1. 核心研究领域：DIU (Document Image Understanding)
**对于属于DIU领域的论文，请放宽筛选标准，只要相关度高都给予及格以上分数。**
- **关注任务**：DocVQA、Information Extraction (VIE/KIE)、Layout Analysis、Table Recognition、OCR。
- **接受范围**：
    - 即使是传统的OCR流水线、或者侧重效率优化（Efficiency）的工作，**也不要排除**，给中等分数即可（因为DIU论文较少，我需要保持关注）。
    - 重点关注：基于VLM的、OCR-free的、端到端的文档理解新工作（给高分）。
- **唯一排除**：**小语种**（非中英）的特定文档数据集或模型（如泰语、越南语等），此类直接打低分。

### 2. 关联领域：LLM / VLM / Agent / Inference Scaling
**对于这些上游或平行领域，我的目的是“寻找工具”，筛选标准需严格。**
我主要寻找**能迁移应用到DIU任务中，提升模型性能（Performance）的方法**，而非提升速度。
- **寻找的技术特性（High Priority）**：
    - **推理阶段干预（Inference-time intervention）**：类似Attention intervention、Logit manipulation、Decoding strategy等。我将其视为提升DIU性能的潜在工具。
    - **Inference Scaling / Reasoning**：CoT、ToT、Search-based reasoning。**关键看它能否帮助解决视觉文档中的复杂逻辑或幻觉问题**。
    - **Agent**：能处理长文档、多步工具调用的Agent架构。
- **排除项（Low Priority）**：
    - 关联领域中纯粹的效率优化（如纯模型量化、剪枝）。
    - 关联领域中过于传统的微调方法或与视觉完全无关的纯NLP理论。

### 📝 打分标准 (0-10分)
- **9-10分 (Must Read)**：
    - **DIU领域**：SOTA级别的VLM文档理解模型、解决了OCR幻觉/细粒度识别/Grounding痛点的DIU工作。
    - **关联领域**：提出了非常新颖的推理阶段干预方法、或极具启发性的多模态Inference Scaling技术，且极大概率能迁移到文档任务。
- **6-8分 (Relevant)**：
    - **DIU领域**：大多数主流DIU工作，包括新数据集、传统方法的改进、效率优化工作。
    - **关联领域**：与视觉多模态紧密相关的VLM改进、Agent框架。
- **3-5分 (Borderline)**：
    - 比较边缘的CV/NLP工作，迁移到文档领域的可能性较低或成本较高。
- **0-2分 (Ignore)**：
    - 小语种工作。
    - 与文档理解毫无关系的纯理论或无关应用（如视频生成、纯自动驾驶、蛋白质折叠）。

### ✅ 任务指令
请根据以上信息，对下面这篇论文进行评估。
1. **Score**: 给出整数评分。
2. **Title_zh**: 将标题翻译为通顺的中文。
3. **Reason**: 用**中文**简述打分理由。如果是DIU论文，指出其任务；如果是关联领域论文，**必须指出其方法论对DIU有何潜在借鉴意义**（如：“此推理干预方法可用于减少OCR幻觉”）。
4. **Summary**: 中文总结核心贡献。
5. **Keywords**: 3-5个中文关键词。
6. **Publication**: 提取会议/期刊（如CVPR, ACL, ICLR），无则填"N/A"。

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
