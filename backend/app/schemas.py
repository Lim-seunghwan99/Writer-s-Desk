from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class WordExampleBase(BaseModel):
    word_example_content: Optional[str] = ""


class WordExampleCreate(WordExampleBase):
    word_example_content: str


class WordExample(WordExampleBase):
    example_sequence: int
    words_id: int

    model_config = {"from_attributes": True}  


class WordExampleUpdate(WordExampleBase):
    pass


# --- Word ---
class WordBase(BaseModel):
    word_name: str
    word_content: Optional[str] = ""


class WordCreate(WordBase):
    user_id: str
    examples: Optional[List[WordExampleCreate]] = Field(
        default=[],
        examples=[ 
            [  
                {"word_example_content": "예시 문장 1입니다."},
                {"word_example_content": "이것은 두 번째 예시 문장입니다."},
            ],
            [{"word_example_content": "또 다른 예시 문장입니다."}],  
        ],
        description="단어에 대한 예문 목록입니다. 각 예문은 'word_example_content' 키를 가져야 합니다.",  
    )


class Word(WordBase):
    words_id: int
    user_id: str
    word_created_time: datetime
    word_count: Optional[int] = 0
    examples: List[WordExample] = []

    model_config = {"from_attributes": True}


class RelatedWordBase(BaseModel):
    form: str
    korean_definition: Optional[str] = None
    usages: Optional[List[str]] = None
    english_definition: Optional[str] = None


class RelatedWord(RelatedWordBase):
    score: Optional[float] = None

    class Config:
        from_attributes = False


class WordRequest(BaseModel):
    query: str = Field(..., description="검색할 핵심 구문 또는 단어")
    target_word_count: int = Field(
        default=5, ge=1, le=20, description="최종적으로 받고 싶은 단어의 수 (1~20)"
    )


class WordResponse(BaseModel):
    query: str
    final_words: List[str]
    target_word_count: int
    source_counts: Dict[str, int]  # 


# --- WordExample Schemas ---
class WordExampleBase(BaseModel):
    """WordExample의 기본 내용 (생성 및 조회 시 공통)"""
    word_example_content: Optional[str] = Field(default="", description="예문 내용")


class WordExampleCreate(WordExampleBase):
    """
    WordExample 생성을 위한 요청 본문 스키마.
    실제 생성될 내용만 포함합니다.
    (words_id와 example_sequence는 경로 및 서버 로직에서 결정)
    """

    pass  


class WordExample(WordExampleBase):
    """
    WordExample 조회(응답)를 위한 스키마.
    DB 모델의 필드를 반영합니다.
    """

    words_id: int
    example_sequence: int

    model_config = {"from_attributes": True}


# --- User ---
class UserBase(BaseModel):
    user_id: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    pass

    model_config = {"from_attributes": True}


# --- Character ---
class CharacterBase(BaseModel):
    character_name: Optional[str] = Field("unnamed", max_length=200)
    character_settings: Optional[str] = ""


class CharacterCreate(CharacterBase):
    pass  


class CharacterUpdate(BaseModel):  
    character_name: Optional[str] = None
    character_settings: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)  


class Character(CharacterBase):
    character_id: int
    works_id: int
    model_config = ConfigDict(from_attributes=True)


# --- World ---
class WorldBase(BaseModel):
    worlds_content: Optional[str] = ""


class WorldCreate(WorldBase):
    pass  


class WorldUpdate(BaseModel):
    worlds_content: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class World(WorldBase):
    worlds_id: int
    works_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Plan ---
class PlanningBase(BaseModel):
    plan_title: Optional[str] = Field("unnamed", max_length=200)
    plan_content: Optional[str] = ""


class PlanningCreate(PlanningBase):
    pass  


class PlanningUpdate(BaseModel):
    plan_title: Optional[str] = None
    plan_content: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class Planning(PlanningBase):
    plan_id: int
    works_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Episode ---
class AIEpisodeContentGenerateRequest(BaseModel):
    additional_prompt: Optional[str] = Field(
        None, description="AI가 콘텐츠를 생성/수정할 때 참고할 추가 프롬프트"
    )


class EpisodeBase(BaseModel):
    works_id: int
    episode_content: Optional[str] = Field(
        None, description="에피소드의 내용"
    )  


class EpisodeCreate(EpisodeBase):
    pass


class Episode(EpisodeBase):
    episode_id: int  

    model_config = ConfigDict(from_attributes=True)  


class EpisodeContentUpdate(BaseModel):
    episode_content: str = Field(..., description="업데이트할 새로운 에피소드 내용")


class EpisodeAIContentResponse(BaseModel):
    episode_id: int
    works_id: int
    updated_episode_content: str = Field(
        description="AI에 의해 생성 또는 수정된 에피소드 내용"
    )

    model_config = ConfigDict(from_attributes=True)  


class EpisodeAIContentResponse(BaseModel):
    episode_id: int
    works_id: int
    updated_episode_content: str

    model_config = ConfigDict(from_attributes=True) 


# --- Work ---
class WorkBase(BaseModel):
    works_title: Optional[str] = Field(
        "unnamed", max_length=200
    )  


class WorkCreate(WorkBase):
    user_id: str  


class Work(WorkBase):
    works_id: int
    user_id: str
    characters: List[Character] = []
    worlds: List[World] = []
    plannings: List[Planning] = []
    episodes: List[Episode] = []

    model_config = ConfigDict(from_attributes=True)


class WorkUpdate(BaseModel):
    works_title: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# --- Dialogue ---
class DialogueContextIDs(BaseModel):
    episode_id: Optional[int] = Field(None, description="참고할 에피소드 ID")
    character_id: Optional[int] = Field(
        None, description="참고할 캐릭터 ID"
    )  
    plan_id: Optional[int] = Field(None, description="참고할 스토리 계획(플롯) ID")


class DialogueGenerationRequest(BaseModel):
    context_ids: DialogueContextIDs = Field(
        ..., description="참고할 컨텐츠들의 ID 정보"
    )
    prompt: str = Field(..., description="생성할 대사에 대한 구체적인 지시")

    class Config:
        json_schema_extra = {
            "example": {
                "context_ids": {"episode_id": 1, "character_id": 1, "plan_id": 1},
                "prompt": "주인공 알렉스가 적에게 마지막 일격을 가하며 외치는 짧고 강렬한 대사를 만들어주세요.",
            }
        }


class DialogueResponse(BaseModel):
    generated_dialogue: str

    class Config:
        json_schema_extra = {"example": {"generated_dialogue": "이것으로... 끝이다!"}}


# 범기님 코드
class ExampleEvaluationRequest(BaseModel):
    sentence: str


# 윤정님 코드
class WordRequestAI(BaseModel):
    word: str


class ExampleResponse(BaseModel):
    word: str
    examples: str
    success: bool
    message: str = ""


class GenerateDialoguePayload(BaseModel):
    episode_content: str = Field(..., description="생성할 에피소드의 핵심 설명")
    additional_prompt: Optional[str] = Field(
        None, description="생성을 위한 추가적인 프롬프트 또는 지시사항"
    )


class ModifyDialoguePayload(BaseModel):
    modification_instruction: str = Field(
        ..., description="현재 대사를 어떻게 수정할지에 대한 구체적인 지시"
    )
    additional_prompt: Optional[str] = Field(
        None, description="수정 시 추가적인 컨텍스트 또는 지시사항"
    )


class EpisodeContentPreview(BaseModel):
    user_input_content: str = Field(description="사용자가 입력한 에피소드 설명/내용")
    generated_dialogue: str = Field(description="AI에 의해 생성된 대사 (미리보기)")
    relevant_context_summary: Optional[List[str]] = Field(
        None, description="대사 생성에 사용된 RAG 컨텍스트 요약 (선택 사항)"
    )
