import logging
import random
import myapikey
from openai import OpenAI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

client = OpenAI(
    api_key=myapikey.API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

SUBJECTS = ["机械制图", "机械基础", "机械制造技术", "数控技术"]

def gen_quiz_prompts(subject, difficulty):
    return f"""
你叫倪珉，是一个机械职业教育的老师
请提出一道机械领域的理论问题
一个问题只能包含一个问句
请确保每次提出不同的问题，涵盖该科目的不同知识点
题库范围是{subject}
难度{difficulty}，数字总共1-1000，越高越难
回复格式"题目: {{题目内容}}"
"""

analysis_prompts = """
你叫倪珉，是一个机械职业教育的老师
分析学生的回答是否正确，并给出简要的解析
1.判断学生的回答属于：【正确】【部分正确】【错误】中的哪一种
2.给出简要解析。若回答错误，需指出错误原因并给出正确答案
3.给出关键词，方便学生复习
回复格式:"【{是否正确}】 分析: {分析内容} \\n 关键词: {关键词}"
"""

answer_prompts = """
你叫倪珉，是一个机械职业教育的老师
请给出下面问题的正确答案
回复格式:"答案: {正确答案}"
"""

if __name__ == "__main__":
    while True:
        # 提问
        subject = random.choice(SUBJECTS)
        difficulty = random.randint(1, 1000)
        logger.debug(f"本次题目科目: {subject} 难度：{difficulty}")
        quiz_prompts = gen_quiz_prompts(subject, difficulty)
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": quiz_prompts}],
            temperature=0.9,
            top_p=0.95
        )
        quiz = completion.choices[0].message.content
        print(quiz)

        # 输入回答
        answer = input("回答> ")

        # 分析回答
        completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "user", "content": analysis_prompts},
                {"role": "assistant", "content": quiz},
                {"role": "user", "content": f"学生回答:{answer}"},
            ],
            temperature=0.7,
            top_p=0.9
        )
        analysis = completion.choices[0].message.content
        print(analysis)

        # 给出正确答案
        completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "user", "content": answer_prompts},
                {"role": "assistant", "content": quiz},
            ],
            temperature=0.7,
            top_p=0.9
        )
        correct_answer = completion.choices[0].message.content
        print(correct_answer)

        # 分割线
        print("-" * 40)