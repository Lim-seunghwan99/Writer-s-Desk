"use client";

import { useSession } from "next-auth/react";
import { useState, useEffect } from "react";
import WordCardWithExamples from "@/components/WordCardWithExamples";
import RelatedWordsModal from "@/components/RelatedWordsModal";
import AiRelatedSearchModal from "@/components/AiRelatedSearchModal";
import AiExampleModal from "@/components/AiExampleModal";
import RelatedByNameModal from "@/components/RelatedByNameModal";
import EasyExampleModal from '@/components/EasyExample';

interface Example {
  word_example_content: string;
  example_sequence: number;
}

interface Word {
  words_id: number;
  word_name: string;
  word_content: string;
  user_id: string;
  word_created_time: string;
  word_count: number;
  examples: Example[];
}

export default function WordPage() {
  const { data: session } = useSession();
  const userId = session?.user?.email ?? "guest";

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [targetWordName, setTargetWordName] = useState("");
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [isAiSearchModalOpen, setIsAiSearchModalOpen] = useState(false);
  const [isAiExampleModalOpen, setIsAiExampleModalOpen] = useState(false);
  const [isRelatedByNameModalOpen, setIsRelatedByNameModalOpen] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [words, setWords] = useState<Word[]>([]);
  const [wordContent, setWordContent] = useState("");
  const [wordName, setWordName] = useState("");
  const [example1, setExample1] = useState("");
  const [example2, setExample2] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResult, setSearchResult] = useState<Word[]>([]);
  const [sortByCount, setSortByCount] = useState(false);

  const fetchWords = async () => {
    try {
      const endpoint = sortByCount
        ? `http://localhost:8000/words/count/${userId}/sort`
        : `http://localhost:8000/words/created_time/${userId}/sort`;

      const res = await fetch(endpoint);
      if (!res.ok) throw new Error(`서버 응답 오류: ${res.status}`);
      const data = await res.json();
      setWords(data);
    } catch (error) {
      console.error("단어 불러오기 실패:", error);
    }
  };

  useEffect(() => {
    if (userId) fetchWords();
  }, [userId, sortByCount]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      alert("검색할 단어를 입력해주세요");
      return;
    }
    try {
      const res = await fetch(
        `http://localhost:8000/words/${userId}/${encodeURIComponent(searchTerm)}`
      );
      if (res.status === 404) {
        alert("해당 단어를 찾을 수 없습니다.");
        setSearchResult([]);
        return;
      }
      if (!res.ok) throw new Error(`검색 실패: ${res.status}`);
      const data = await res.json();
      setSearchResult([data]);
    } catch (error) {
      console.error("단어 검색 실패:", error);
      alert("단어 검색 실패");
      setSearchResult([]);
    }
  };

  const handlePost = async () => {
    if (!userId) {
      alert("로그인이 필요합니다.");
      return;
    }
    if (!wordName.trim()) {
      alert("단어를 입력해주세요");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/words/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          word_name: wordName,
          word_content: wordContent,
          user_id: userId,
          examples: [
            { word_example_content: example1 },
            { word_example_content: example2 },
          ],
        }),
      });
      const data = await response.json();
      alert("단어가 등록되었습니다!");
      await fetchWords();
      setWordName("");
      setWordContent("");
      setExample1("");
      setExample2("");
    } catch (error) {
      console.error("단어 등록 실패:", error);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">단어 등록</h2>

      <input
        type="text"
        placeholder="단어 입력"
        value={wordName}
        onChange={(e) => setWordName(e.target.value)}
        className="w-full px-3 py-2 rounded mb-2"
      />
      <input
        type="text"
        placeholder="단어 설명"
        value={wordContent}
        onChange={(e) => setWordContent(e.target.value)}
        className="w-full px-3 py-2 rounded mb-2"
      />
      <input
        type="text"
        placeholder="예시 1"
        value={example1}
        onChange={(e) => setExample1(e.target.value)}
        className="w-full px-3 py-2 rounded mb-2"
      />
      <input
        type="text"
        placeholder="예시 2"
        value={example2}
        onChange={(e) => setExample2(e.target.value)}
        className="w-full px-3 py-2 rounded mb-4"
      />
      <button
        onClick={handlePost}
        className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
      >
        단어 등록하기
      </button>

      <button
        onClick={() => setIsSearchModalOpen(true)}
        className="bg-blue-500 text-white px-4 py-2 rounded mb-6 ml-2"
      >
        단어 검색
      </button>

      <button
        className="bg-blue-500 text-white px-4 py-2 rounded mb-6 ml-2"
        onClick={() => setShowModal(true)}
      >
        쉬운 설명 생성
      </button>

      {showModal && <EasyExampleModal onClose={() => setShowModal(false)} />}

      <button
        onClick={() => setIsAiSearchModalOpen(true)}
        className="bg-purple-600 text-white px-4 py-2 rounded ml-2"
      >
        🤖 AI 단어 추천 검색
      </button>

      <button
        onClick={() => setIsRelatedByNameModalOpen(true)}
        className="bg-purple-600 text-white px-4 py-2 rounded ml-2"
      >
        🤖 AI 단어 이름으로 관련 단어 검색
      </button>

      <button
        onClick={() => setIsAiExampleModalOpen(true)}
        className='bg-purple-600 text-white px-4 py-2 rounded ml-2'
      >
        🤖 AI 예문 생성
      </button>

      <RelatedByNameModal
      isOpen={isRelatedByNameModalOpen}
      onClose={() => setIsRelatedByNameModalOpen(false)}
      /> 

      <AiExampleModal
        isOpen={isAiExampleModalOpen}
        onClose={() => setIsAiExampleModalOpen(false)}
      />

      <AiRelatedSearchModal
        isOpen={isAiSearchModalOpen}
        onClose={() => setIsAiSearchModalOpen(false)}
      />

      <RelatedWordsModal
        targetWord={targetWordName}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />

      {isSearchModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-full max-w-md relative">
            <button
              onClick={() => setIsSearchModalOpen(false)}
              className="absolute top-2 right-2 text-gray-500 hover:text-black"
            >
              ✕
            </button>
            <h2 className="text-xl font-bold mb-4">단어 검색</h2>
            <input
              type="text"
              placeholder="검색할 단어 입력"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 rounded border mb-4"
            />
            <button
              onClick={async () => {
                await handleSearch();
                setIsSearchModalOpen(false);
              }}
              className="bg-blue-500 text-white px-4 py-2 rounded w-full"
            >
              검색하기
            </button>
          </div>
        </div>
      )}

      {searchResult.length > 0 && (
        <div className="mt-8 space-y-4">
          <h1 className="text-2xl font-bold mb-2">🔍 검색 결과</h1>
          {searchResult.map((word) => (
            <div key={word.words_id}>
              <WordCardWithExamples word={word} />
              <button
                onClick={() => {
                  setTargetWordName(word.word_name);
                  setIsModalOpen(true);
                }}
                className="mt-2 text-sm text-blue-500 underline"
              >
                관련 단어 보기
              </button>
            </div>
          ))}
          <button
            onClick={() => setSearchResult([])}
            className="text-sm text-gray-500 underline"
          >
            검색 결과 초기화
          </button>
        </div>
      )}

      <div className="mt-8 space-y-4">
        <h1 className="text-2xl font-bold mb-4">📘 단어 목록</h1>

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setSortByCount(false)}
            className={`px-4 py-2 rounded text-white ${!sortByCount ? "bg-blue-500" : "bg-gray-400"}`}
          >
            최신순 보기
          </button>
          <button
            onClick={() => setSortByCount(true)}
            className={`px-4 py-2 rounded text-white ${sortByCount ? "bg-blue-500" : "bg-gray-400"}`}
          >
            조회수순 보기
          </button>
        </div>

        {words.length === 0 ? (
          <p>단어가 없습니다.</p>
        ) : (
          words.map((word) => (
            <div key={word.words_id}>
              <WordCardWithExamples word={word} />
              <button
                onClick={() => {
                  setTargetWordName(word.word_name);
                  setIsModalOpen(true);
                }}
                className="mt-2 text-sm text-blue-500 underline"
              >
                관련 단어 보기
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}