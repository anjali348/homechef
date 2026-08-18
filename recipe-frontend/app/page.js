"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [ingredients, setIngredients] = useState([]);
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [results, setResults] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/ingredients")
      .then((res) => res.json())
      .then((data) => setSuggestions(data));
  }, []);

  useEffect(() => {
    if (ingredients.length === 0) {
      setResults([]);
      return;
    }
    fetch("http://localhost:8000/pantry-match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ have: ingredients, k: 10 }),
    })
      .then((res) => res.json())
      .then((data) => setResults(data));
  }, [ingredients]);

  function addIngredient() {
    const trimmed = input.trim();
    if (trimmed && !ingredients.includes(trimmed)) {
      setIngredients([...ingredients, trimmed]);
    }
    setInput("");
  }

  function removeIngredient(item) {
    setIngredients(ingredients.filter((i) => i !== item));
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="font-serif text-3xl text-[#3A322A] mb-1">What's in your kitchen?</h1>
      <p className="text-[#8A7E70] mb-6">Add what you have — we'll find what you can cook.</p>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && addIngredient()}
        placeholder="Add an ingredient and press Enter"
        list="ingredient-suggestions"
        className="w-full rounded-lg border border-[#E4DAcc] bg-white px-4 py-2.5 text-[#3A322A] outline-none focus:border-[#3F6B3F]"
      />
      <datalist id="ingredient-suggestions">
        {suggestions.map((s) => (
          <option key={s} value={s} />
        ))}
      </datalist>

      <div className="mt-3 flex flex-wrap gap-2">
        {ingredients.map((item) => (
          <span
            key={item}
            onClick={() => removeIngredient(item)}
            className="cursor-pointer rounded-full bg-[#EDE4D3] px-3 py-1 text-sm text-[#3A322A] hover:bg-[#E0D3BC]"
          >
            {item} ✕
          </span>
        ))}
      </div>

      <div className="mt-8 space-y-3">
        {results.map((r) => (
          <div
            key={r.id}
            className="rounded-xl border border-[#EAE0D0] bg-white p-4 shadow-sm"
          >
            <h3 className="font-serif text-lg text-[#3A322A]">{r.title}</h3>
            {r.missing.length > 0 && (
              <p className="mt-1 text-sm text-[#C4703E]">
                Missing: {r.missing.join(", ")}
              </p>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}