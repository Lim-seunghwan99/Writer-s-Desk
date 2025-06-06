from openai import OpenAI
from dotenv import load_dotenv
from .config import OPENAI_API_KEY, AI_UTILS_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)
import re

load_dotenv()


def generate_examples_with_gpt(prompt_text: str) -> list[str]:
    prompt = f"'{prompt_text}'라는 단어에 대한 예시 문장을 2개 만들어줘. 각 문장은 한 줄씩 따로 써줘."
    response = client.chat.completions.create(
        model=AI_UTILS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150,
    )
    result = response.choices[0].message.content.strip()
    return [line.strip() for line in result.split("\n") if line.strip()]


def evaluate_sentence_with_gpt(sentence: str) -> str:
    prompt = f'다음 문장을 평가해줘:\n"{sentence}"\n논리성, 문법, 표현력 등을 고려해서 평가해줘. 간결하게.'
    response = client.chat.completions.create(
        model=AI_UTILS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def clean_evaluation_response(text: str) -> str:
    text = text.replace("\\n", " ").replace("\n", " ").strip()
    text = text.replace('\\"', '"')
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def evaluate_user_example(word: str, sentence: str) -> str:
    prompt = (
        f"다음 문장은 '{word}'라는 단어를 포함해서 작성된 문장입니다:\n"
        f'"{sentence}"\n'
        "문장이 자연스럽고 의미가 통하는지 평가해주세요. "
        "문법, 표현, 의미 전달력을 고려해서 평가하고, 개선할 부분이 있다면 간단히 조언해주세요."
    )
    response = client.chat.completions.create(
        model=AI_UTILS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=200,
    )
    raw_text = response.choices[0].message.content.strip()
    return clean_evaluation_response(raw_text)  # ✅ 후처리 적용


