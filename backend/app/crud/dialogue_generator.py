from openai import OpenAI
from app.config import OPENAI_API_KEY, DIALOGUE_LLM_MODEL, DIALOGUE_LLM_TEMP

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Warning: OPENAI_API_KEY is not set. Dialogue generation will not work.")
    client = None


def generate_dialogue_from_context(
    worlds_content: str,
    episode_content: str,
    character_settings: str,
    plan_content: str,
    prompt: str,
) -> str:
    if not client:
        raise ConnectionError("OpenAI client is not initialized. Check API key.")

    system_message = """
    당신은 창의적인 스토리 작가입니다. 주어진 세계관, 에피소드 내용, 캐릭터 설정, 스토리 계획을 바탕으로,
    사용자의 요청에 가장 적합하고 자연스러운 대사를 생성해야 합니다.
    대사는 캐릭터의 성격과 현재 상황에 잘 어울려야 하며, 전체 이야기의 흐름에 기여해야 합니다.
    생성된 대사만을 응답으로 반환하고, 다른 부가적인 설명은 포함하지 마십시오.
    """

    full_prompt = f"""
    ### 지시사항
    다음 정보를 바탕으로 사용자의 요청에 맞는 캐릭터 대사를 생성해주세요.

    ### 세계관 배경
    {worlds_content}

    ### 현재 에피소드 주요 내용
    {episode_content}

    ### 관련 캐릭터 설정
    {character_settings}

    ### 현재 장면 또는 스토리 계획
    {plan_content}

    ### 사용자 요청 (생성할 대사에 대한 구체적인 지시)
    {prompt}

    ### 생성할 대사:
    """  

    try:
        response = client.chat.completions.create(
            model=DIALOGUE_LLM_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": full_prompt},
            ],
            temperature=DIALOGUE_LLM_TEMP,
            max_tokens=200,  
        )
        generated_text = response.choices[0].message.content.strip()
        return generated_text
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        raise  
