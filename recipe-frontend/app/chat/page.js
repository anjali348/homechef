"use client";

import { useState } from "react";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  function askQuestion() {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer(null);
    fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, k: 4 }),
    })
      .then((res) => res.json())
      .then((data) => {
        setAnswer(data.answer);
        setSources(data.sources);
      })
      .finally(() => setLoading(false));
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="font-serif text-3xl text-[#3A322A] mb-1">Ask about your recipes</h1>
      <p className="text-[#8A7E70] mb-6">Substitutions, ideas, what goes with what.</p>

      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && askQuestion()}
        placeholder="e.g. what can I make with chickpeas and spinach?"
        className="w-full rounded-lg border border-[#E4DAcc] bg-white px-4 py-2.5 text-[#3A322A] outline-none focus:border-[#3F6B3F]"
      />
      <button
        onClick={askQuestion}
        className="mt-3 rounded-lg bg-[#3F6B3F] px-5 py-2.5 text-white hover:bg-[#2F512F]"
      >
        Ask
      </button>

      {loading && <p className="mt-6 text-[#8A7E70]">Thinking…</p>}

      {answer && (
        <div className="mt-6 rounded-xl border border-[#EAE0D0] bg-white p-5 shadow-sm">
          <p className="leading-relaxed text-[#3A322A]">{answer}</p>
          {sources.length > 0 && (
            <p className="mt-4 text-sm text-[#8A7E70]">
              Sources: {sources.map((s) => s.title).join(", ")}
            </p>
          )}
        </div>
      )}
    </main>
  );
}