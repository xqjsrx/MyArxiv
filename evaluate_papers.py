import os
import json
from openai import OpenAI

# 填写API的密钥
API_KEY = os.getenv("API_KEY")

# 自定义的提示模板
PROMPT_TEMPLATE = """
我是一个人工智能相关专业在读研究生，目前的研究内容是文档图片理解（document image understanding, DIU），DIU的目标是输入一张文档（账单、简历、菜单等）的图片，AI能够识别里面的信息，理解这个文档的含义，比如这是什么种类的文档、里面的字段有哪些、这些字段之间的关系是什么之类的。

想要实现DIU，一般需要三个步骤：
1、ocr：将文档里的文本识别出来，这一步有些论文的做法是使用ocr工具，另外一些ocr free的论文则在模型里实现了ocr的功能，不需要ocr工具。除了OCR Free的工作，针对性增强OCR能力的工作值得关注。
2、实体识别：将上文得到的文本进行实体识别。在这个步骤中，有一些经典的主题，例如开放域实体识别，生成式实体识别，以及少样本乃至零样本识别。
3、关系抽取：将上文得到的实体识别结果进行关系抽取。在这个步骤中，性能指标达到先进水平的工作值得关注。在降低计算复杂度方面的工作值得关注。在减少累积误差的工作值得关注。

除了任务层面以外，还有一类论文值得关注。之前主流的论文主要使用预训练模型搭建一个系统，而近期随着多模态模型的出现，使用多模态模型（如VLM）进行DIU的工作出现了很多，他们直接训练或微调了一个视觉多模态模型进行DIU，不需要分步骤，一次实现识别，甚至可以作为聊天机器人进行问答。这可能是未来的发展趋势，这些论文证明了可以应用完全不同的技术栈在该领域内进行颠覆式的创新，值得重点关注。
最后，那些提出这个领域内新数据集的工作值得关注。

除了直接进行DIU工作的论文，一些相领域或关键词的工作也值得借鉴，比如视觉信息抽取（visual information extraction）、visually-rich document、布局（layout）、表格（table）等。

以上是DIU领域的概述，此外，（视觉）多模态模型（VLM）、大语言模型（LLM）作为DIU的上游领域，其中的新任务、新技术的提出可能可以应用在DIU领域。其中有潜力的一条技术路线如下：目前，LLM的发展已经到了inference scaling的阶段，即通过增大推理阶段的计算量来提高模型的性能，比如chain of thought(cot)、tree of thought(tot)、contrastive decoding、gpt o1、mcts、test time training(ttt)等技术都是这一阶段的热门技术，目前这些技术主要应用于需要逻辑推理（reasoning）的领域，而我觉得这些技术可以提高VLM在DIU领域的性能，值得重点关注。

近期，agent（智能体）的概念火热了起来，智能体（Intelligent Agent）是一种具有自主性、感知能力、学习能力和适应性的计算机程序或系统。它可以在某种程度上理解其所处的环境，根据环境的变化做出相应的决策和行动，以实现某种预定的目标。公认的agent系统由智能体（一般是LLM担任）、记忆、工具、规划、行动等要素组成。我觉得agent是人工智能的下一个阶段，搭建一个应用于DIU的agent应该是一个不错的想法。目前，agent的工作还在比较早期的阶段，大致有两个研究方向：应用型主要研究使用针对特定领域搭建一个agent系统，类似我设想的DIU agent；研究型主要研究解决目前agent的不足，比如核心LLM的多步推理操作能力等。agent值得关注。

你是我的助手，我需要你帮我从每天新发布的论文中进行筛选，帮我选出那些值得阅读的论文，也就是DIU相关的论文、VLM和LLM中inference scaling、reasoning相关的论文、agent相关的论文，请注意相关指的是有极其紧密的关系，可以直接应用在DIU领域上，不能直接迁移应用视作不相关。对于和以上领域没有直接关联的论文，请排除在外。我会提供每篇论文的信息，请根据这篇论文是否值得阅读对论文进行评分，满分10分，分数为整数，并给出简短的打分的理由，然后写一个这篇论文的简短概括。

请注意，部分论文在comment中会表明已被某些期刊或会议接受，如果是CCF A类等顶刊顶会，请适当加分；如果论文在abstract中表示已开源，请适当加分。打分不要太中庸，需要有区分度。

下面，请根据以下论文信息进行评分：
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
  "reason": "xxx",
  "summary": "xxx"
}
"""

def call_qwen_api(prompt):
    try:
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        completion = client.chat.completions.create(
            model="qwen-turbo-latest",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"错误信息：{e}")
        print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
        return None

def clean_json_response(response):
    # 清理响应内容，只保留 JSON 部分
    start_index = response.find("{")
    end_index = response.rfind("}") + 1
    if start_index != -1 and end_index != -1:
        return response[start_index:end_index]
    return None

def evaluate_papers(input_file, output_file):
    with open(input_file, 'r') as f:
        papers = json.load(f)

    for paper in papers:
        # 构建提示
        prompt = PROMPT_TEMPLATE.format(
            title=paper['title'],
            authors=', '.join(paper['authors']),
            abstract=paper['abstract'],
            comment=paper.get('comment', ''),
            category=paper['category'],
        )
        prompt = prompt + JSON_RESPONSE_TEMPLATE
        print(prompt)
        # 调用 API 并获取评分
        res = call_qwen_api(prompt)
        print(res)
        if res:
            cleaned_res = clean_json_response(res)
            if cleaned_res:
                try:
                    # 解析 JSON 响应
                    response = json.loads(cleaned_res)
                    # 添加评分到论文信息中
                    paper['score'] = response['score']
                    paper['reason'] = response['reason']
                    paper['summary'] = response['summary']
                except json.JSONDecodeError as e:
                    print(f"解析 JSON 失败：{e}")
                    print(f"响应内容：{cleaned_res}")
                    # 重新发送请求
                    res = call_qwen_api(prompt)
                    if res:
                        cleaned_res = clean_json_response(res)
                        if cleaned_res:
                            try:
                                response = json.loads(cleaned_res)
                                paper['score'] = response['score']
                                paper['reason'] = response['reason']
                                paper['summary'] = response['summary']
                            except json.JSONDecodeError as e:
                                print(f"再次解析 JSON 失败：{e}")
                                print(f"再次响应内容：{cleaned_res}")
            else:
                print("未找到有效的 JSON 内容")
        print(paper)

    # 写入输出文件
    with open(output_file, 'w') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print(API_KEY)
    evaluate_papers("target/latest_papers.json", "target/evaluated_papers.json")
