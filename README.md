# 📚 Writer's Desk

<p>작가를 위한 AI 기능이 포함된 단어장 서비스입니다.  </p>
<p>작가들이 단어를 등록하고 관리할 수 있는 단어장 서비스로, 작품 설정, 등장인물 관리, 에피소드 작성 등 다양한 기능을 제공합니다.</p>
<p>이 서비스는 AI 기능을 통해 단어의 예시 문장을 자동 생성하고, 연관 단어를 추천하는 등 작가의 창작 과정을 도와줍니다.</p>
<p>캐릭터 이미지 생성 기능도 포함되어 있어, 작가가 설정한 캐릭터의 외형을 AI가 자동으로 생성해줍니다.</p>
<p>총 4명이 협업하여 프론트엔드, 백엔드, AI 기능 및 시스템 아키텍처를 구성했습니다.</p>
<p>대표적인 AI 기능으로는 <strong>AI Graph(DuckDuckGo를 통한 웹 검색, OpenSearch, RAG 기반의 단어, LLM을 이용한 단어 추출)</strong>로 유사한 단어 검색 기능,</p>
<p>세계관, 캐릭터, 에피소드를 생성할 때, <strong>OpenSearch VectorDB로 임베딩을</strong> 하고, </p>
<p>에피소드를 생성할 때 RAG 기반으로 해당 정보를 받아와 LLM을 통해 에피소드 예시를 생성하는 기능 등이 있습니다.</p>

---

## 📖 프로젝트 소개
<p>기간 : 2025.05.19 ~ 2025.06.05</p>
<p>인원 : 4명</p>
<p>Writer's Desk는 작가들이 단어를 등록하고 관리할 수 있는 단어장 서비스입니다.</p>
<p>작품 설정, 등장인물 관리, 에피소드 작성 등 작가의 창작 활동을 지원하는 다양한 기능을 제공합니다.</p>
<p>이 서비스는 AI 기능을 통해 단어의 예시 문장을 자동 생성하고, 연관 단어를 추천하는 등 작가의 창작 과정을 도와줍니다.</p>
<p>캐릭터 이미지 생성 기능도 포함되어 있어, 작가가 설정한 캐릭터의 외형을 AI가 자동으로 생성해줍니다.</p>
<p>임베딩 데이터 : 한글 사전 데이터</p>
<p>https://huggingface.co/datasets/binjang/NIKL-korean-english-dictionary/viewer/default/train?p=531&views%5B%5D=train</p>
<p>임베딩 모델 : https://huggingface.co/snunlp/KR-SBERT-V40K-klueNLI-augSTS</p>
<p>LLM 모델 : GPT-4o-mini</p>

---

## 🛠️ 기술 스택

- **Frontend**: Next.js, Tailwind CSS, TypeScript  
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy
- **AI**: Hugging Face Transformers, AI Agent(LangChain, LangGraph), OpenSearch, ComfyUI 기반 이미지 생성  
- **DevOps**: Docker, REST API, Docker Compose, OpenSearch

---

## 👨‍👩‍👧‍👦 팀 구성

| 이름 | 역할 |
|------|------|
| 임승환 | 백엔드 FAST API API 개발, DevOps 기반 시스템 아키텍처 설계 및 구축, 데이터베이스 설계, AI Agent API(RAG, Web Search, LLM기반) 개발 |
| 장유진 | 프론트 Next.js 개발, 게스트 로그인, 구글 로그인 구현, DB Docker 기반 컨테이너 구축 |
| 박범기 | Comfy UI 기반 이미지 생성 기능 구현, LLM 기반 유사도 검색 기능 등 AI 기능 구현, 백엔드 API 개발 | 
| 정윤정 | Figma, ppt, UI, LLM 기반 AI 예문 생성기능, LLM 기반 단어 설명 기능 등 AI 기능 구현, 백엔드 API 개발 | 

---

### AI Agent 그래프
![AI Agent](datas/project4_AIAgent2.png)


### 시스템 아키텍처
![System Architecture](datas/project4_drawio2.png)

---

## 🤖 AI 기능

- 예시 문장 자동 생성 (AI 기반)  
  ![Generate AI Example](datas/generate_ai_usages.gif)

- AI 에이전트 동작  
  ![AI Agent](datas/word_search_ai_relate.gif)




## 📚 주요 기능 및 서비스 화면

<div align="center">
  <table>
    <tr align="center">
      <td><strong>🤖 RAG/LLM 기반 예시 문장 생성</strong></td>
      <td><strong>🧠 AI 유사 단어 검색</strong></td>
      <td><strong>🔒 간편 소셜 로그인</strong></td>
    </tr>
    <tr>
      <td><img src="datas/generate_ai_usages.gif" height="320px" width="240px" /></td>
      <td><img src="datas/ai_search_simillar.gif" height="320px" width="240px" /></td>
      <td><img src="datas/google_login.gif" height="320px" width="240px" /></td>
    </tr>
    <tr>
      <td align="left">작가가 글을 쓸 때 막히는 부분을 해소할 수 있도록, 입력한 단어의 의미와 뉘앙스에 맞는 예시 문장을 RAG 및 LLM   기술을 활용하여 동적으로 생성해줍니다.</td>
      <td align="left">문맥적으로 유사하거나 연상되는 단어들을 LLM이 추론하여 제시합니다.</td>
      <td align="left">별도의 회원가입 절차 없이, 사용자가 기존에 사용하던 구글 계정을 서비스에 로그인할 수 있는 기능을 제공합니다.</td>
    </tr>
  </table>
  <table>
  <tr align="center">
    <td><strong>✍️ 나만의 단어 등록</strong></td>
    <td><strong>📊 직관적인 단어 정렬</strong></td>
    <td><strong>🔍 빠른 단어 검색</strong></td>
  </tr>
  <tr>
    <td><img src="datas/post_word.gif" height="320px" width="240px" /></td>
    <td><img src="datas/sort_word_detail.gif" height="320px" width="240px" /></td>
    <td><img src="datas/search_word.gif" height="320px" width="240px" /></td>
  </tr>
  <tr>
    <td align="left">자신만의 단어, 의미, 예시 문장을 추가하여 개인화된 단어장을 만들고 관리할 수 있습니다.</td>
    <td align="left">등록한 단어들을 조회수, 생성일(최신순/오래된순) 등 다양한 기준에 따라 정렬할 수 있습니다.</td>
  <td align="left">단어장에 등록된 단어 중에서 원하는 단어를 찾아볼 수 있는 기능을 제공합니다.</td>
  </tr>
</table>
  <table>
  <tr align="center">
    <td><strong>🔗 AI 연관 단어 추천</strong></td>
    <td><strong>📖 작품 정보 등록</strong></td>
    <td><strong>🌍 세계관 설정 및 관리</strong></td>
  </tr>
  <tr>
    <td><img src="datas/word_search_ai_relate.gif" height="320px" width="240px" /></td>
    <td><img src="datas/post_work.gif" height="320px" width="240px" /></td>
    <td><img src="datas/post_world.gif" height="320px" width="240px" /></td>
  </tr>
  <tr>
    <td align="left">입력한 단어와 관련된 새로운 아이디어를 얻을 수 있도록, Rag, WebSearch, LLM으로 구성된 AI Agent기반의 단어 추천이 이루어집니다.</td>
    <td align="left">작품에 사용될 설정, 등장인물, 세계관 등을 체계적으로 관리할 수 있습니다.</  td>
  <td align="left">작품의 배경이 되는 독창적인 세계관을 생성하고 상세 설정을 추가할 수 있습니다.</td>
</tr>
  </table>
<table>
  <tr align="center">
    <td><strong>📜 에피소드 추가</strong></td>
    <td><strong>💡 기획 및 아이디어 추가</strong></td>
    <td><strong>👤 캐릭터 생성 및 연결</strong></td>
  </tr>
  <tr>
    <td><img src="datas/post_episode.gif" height="320px" width="240px" /></td>
    <td><img src="datas/post_planning.gif" height="320px" width="240px" /></td>
    <td><img src="datas/post_character.gif" height="320px" width="240px" /></td>
  </tr>
  <tr>
    <td align="left">작품의 스토리를 구성하는 개별 에피소드를 추가할 수 있습니다. </td>
    <td align="left">구체적인 기획 내용을 추가하고 관리하여 창작의 초기 단계를 체계적으로 정리할 수 있습니다.</td>
    <td align="left">작품에 등장하는 새로운 캐릭터를 생성하고, 해당 캐릭터가 속한 작품이나 등장하는 에피소드에 연결하여 관계를 설정할 수 있습니다.</td>
  </tr>
  </table>
<table>
  <tr align="center">
    <td><strong>🎭 캐릭터 정보 수정</strong></td>
    <td><strong>🎨 AI 캐릭터 이미지 생성</strong></td>
    <td><strong>🤖 RAG/LLM 기반 예시 문장 생성</strong></td>
  </tr>
  <tr>
    <td><img src="datas/put_character.gif" height="320px" width="240px" /></td>
    <td><img src="datas/create_character_image.gif" height="320px" width="240px" /></td>
    <td><img src="datas/generate_ai_usages.gif" height="320px" width="240px" /></td>
  </tr>
  <tr>
    <td align="left">이미 등록된 캐릭터의 정보를 수정할 수 있습니다.</td>
    <td align="left">캐릭터의 외형 묘사를 기반으로, AI 이미지 생성 모델이 캐릭터의 초상화를 그려줍니다.</td>
    <td align="left">미관상의 문제로 중복된 기능을 다시 넣었습니다, ai 예문 생성.</td>
  </tr>
  </table>
</div>
  
  
  ### 포팅 메뉴얼
  1. **포팅 환경 설정**
     - Docker와 Docker Compose가 설치되어 있어야 합니다.
     - PostgreSQL 데이터베이스를 설정합니다.
  
  2. **프로젝트 설치**
      - cd backend
      - docker-compose up -d (linux 환경에서 실행)
      - pip install -r requirements.txt

      cd frontend
      - npm install
      - npm run dev


    
### API 명세서
![API1](datas/api_1.png)
![API2](datas/api_2.png)


### env 파일 설정(root 디렉토리에 .env 파일 생성)
```python
DATABASE_URL="postgresql://username:password@localhost:5432/word"

TAVILY_API_KEY = "your_tavily_api_key_here"


OPENAI_API_KEY="your_openai_api_key_here"

OPENSEARCH_SINGLE_HOST="localhost"
OPENSEARCH_SINGLE_PORT="9200"
OPENSEARCH_USER="your_opensearch_username"
OPENSEARCH_PASSWORD="your_opensearch_password"
OPENSEARCH_INDEX_NAME="korean-english-dictionary"
EMBEDDING_MODEL_NAME="snunlp/KR-SBERT-V40K-klueNLI-augSTS"
OPENSEARCH_RAG_INDEX_NAME="your_rag_index_name_here"

# 웹 검색 노드에서 사용할 LLM 설정
MODEL_NAME  = "gpt-4o-mini" 
LLM_WEB_SEARCH_MODEL_NAME=${MODEL_NAME} 
LLM_WEB_SEARCH_TEMPERATURE=0.0

# 단어 생성 노드에서 사용할 LLM 설정
LLM_GENERATE_MODEL_NAME=${MODEL_NAME} 
LLM_GENERATE_TEMPERATURE=0.1

# 대사 생성용 LLM 설정
DIALOGUE_LLM_MODEL_NAME=${MODEL_NAME} # 또는 다른 원하는 모델
DIALOGUE_LLM_TEMPERATURE=0.7
```