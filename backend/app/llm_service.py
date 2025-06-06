# app/llm_service.py
import openai
from typing import List, Dict, Any, Optional
from . import config
if config.OPENAI_API_KEY:
    pass
else:
    print(
        "Warning: OPENAI_API_KEY not set in .env or config. LLM calls will likely fail."
    )


class LLMService:
    def _construct_prompt_for_generation(  
        self,
        relevant_docs: List[Dict[str, Any]],
        user_provided_context: str,
        additional_prompt: Optional[str] = None,
    ) -> str:
        context_str = "다음은 이 이야기의 캐릭터 및 세계관에 대한 참고 정보입니다:\n"
        characters_info = []
        worlds_info = []

        for doc in relevant_docs:
            if doc["content_type"] == "character":
                characters_info.append(f"- {doc['text_content']}")
            elif doc["content_type"] == "world":
                worlds_info.append(f"- 세계관 설정: {doc['text_content']}")

        if characters_info:
            context_str += "등장인물 정보:\n" + "\n".join(characters_info) + "\n\n"
        if worlds_info:
            context_str += "세계관 정보:\n" + "\n".join(worlds_info) + "\n\n"

        if not characters_info and not worlds_info:
            context_str = "참고할 만한 특정 캐릭터 또는 세계관 정보가 검색되지 않았습니다. 주어진 사용자 제공 컨텍스트에 최대한 기반하여 생성해주세요.\n\n"

        additional_prompt_text = ""
        if additional_prompt:
            additional_prompt_text = f'\n추가 지시사항: "{additional_prompt}"\n'

        prompt = (
            f"{context_str}"
            f"위 정보를 바탕으로 다음 사용자 제공 컨텍스트를 위한 대사를 생성해주세요. "
            f"대사는 등장인물 간의 자연스러운 대화 형식이어야 하며, 필요한 경우 (지문)도 포함될 수 있습니다. "
            f"결과는 대사만 포함해주세요.\n"
            f'사용자 제공 컨텍스트: "{user_provided_context}"\n'
            f"{additional_prompt_text}"
            f"생성된 대사:"
        )
        return prompt

    def _construct_prompt_for_modification(
        self,
        relevant_docs: List[Dict[str, Any]],
        parsed_original_description: str,
        current_dialogue: str,
        modification_instruction: str,  
        additional_prompt: Optional[str] = None,
    ) -> str:
        context_str = "다음은 이 이야기의 캐릭터 및 세계관에 대한 참고 정보입니다:\n"
        characters_info = []
        worlds_info = []
        for doc in relevant_docs:
            if doc["content_type"] == "character":
                characters_info.append(f"- {doc['text_content']}")
            elif doc["content_type"] == "world":
                worlds_info.append(f"- 세계관 설정: {doc['text_content']}")

        if characters_info:
            context_str += "등장인물 정보:\n" + "\n".join(characters_info) + "\n\n"
        if worlds_info:
            context_str += "세계관 정보:\n" + "\n".join(worlds_info) + "\n\n"

        if not characters_info and not worlds_info:
            context_str = (
                "참고할 만한 특정 캐릭터 또는 세계관 정보가 검색되지 않았습니다.\n\n"
            )

        additional_prompt_text = ""
        if additional_prompt:
            additional_prompt_text = f'\n수정 시 추가 고려사항: "{additional_prompt}"\n'

        prompt = (
            f"{context_str}"
            f'원래 에피소드 설명 (파싱된 내용): "{parsed_original_description}"\n\n'
            f'현재 대사:\n"""\n{current_dialogue}\n"""\n\n'
            f'사용자 수정 요청: "{modification_instruction}"\n'
            f"{additional_prompt_text}"
            f"위 캐릭터/세계관 정보와 원래 에피소드 설명을 참고하여, 현재 대사를 사용자의 수정 요청에 맞게 자연스럽게 수정해주세요. "
            f"수정된 전체 대사만 반환해주세요:\n\n"
            f"수정된 대사:"
        )
        return prompt

    def _call_llm(self, prompt: str, temperature: float) -> str:
        if not config.OPENAI_API_KEY:
            error_msg = "LLM Error: OPENAI_API_KEY is not configured."
            print(error_msg)
            return error_msg
        print("--- LLM PROMPT ---")
        print(prompt)
        print(f"--- Model: {config.DIALOGUE_LLM_MODEL}, Temperature: {temperature} ---")
        print("------------------")
        try:
            client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=config.DIALOGUE_LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 이야기의 대사를 창의적으로 작성하는 전문 작가입니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = f"LLM API call failed: {e}"
            print(error_msg)
            return error_msg

    def generate_dialogue(  
        self,
        relevant_docs: List[Dict[str, Any]],
        user_provided_context: str,
        additional_prompt: Optional[str] = None,
    ) -> str:
        prompt = self._construct_prompt_for_generation(  
            relevant_docs,
            user_provided_context,
            additional_prompt,
        )
        return self._call_llm(prompt, temperature=config.DIALOGUE_LLM_TEMP)
    def modify_dialogue(
        self,
        relevant_docs: List[Dict[str, Any]],
        parsed_original_description: str,
        current_dialogue: str,
        modification_instruction: str,  
        additional_prompt: Optional[str] = None,
    ) -> str:
        prompt = self._construct_prompt_for_modification(
            relevant_docs,
            parsed_original_description,
            current_dialogue,
            modification_instruction,  
            additional_prompt,
        )
        return self._call_llm(prompt, temperature=config.DIALOGUE_LLM_TEMP)
    
    
llm_service = LLMService()
