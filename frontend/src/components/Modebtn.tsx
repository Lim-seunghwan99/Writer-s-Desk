import Link from "next/link"

export default function Modebtn() {
    return(
        <div className="flex justify-end gap-2 mb-6">
        <button className="px-4 py-1 bg-gray-100 text-sm rounded hover:bg-gray-200">
            <Link href="/word">AI 사전</Link>
        </button>
        <button className="px-4 py-1 bg-black text-white text-sm rounded hover:bg-gray-800">
            <Link href="/works"> 인물 맞춤 대사  </Link>
        </button>
      </div>
) 
}