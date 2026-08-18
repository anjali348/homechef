"use client";

import { useState } from "react";

export default function AddRecipe() {
  const [title, setTitle] = useState("");
  const [ingredients, setIngredients] = useState("");
  const [steps, setSteps] = useState("");
  const [status, setStatus] = useState(null);

  function submitRecipe() {
    if (!title.trim()) {
      setStatus("Please add a title first.");
      return;
    }
    const ingredientList = ingredients.split("\n").map((s) => s.trim()).filter(Boolean);
    const stepList = steps.split("\n").map((s) => s.trim()).filter(Boolean);

    fetch("http://localhost:8000/recipes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: title,
        ingredients: ingredientList,
        ner: ingredientList,
        steps: stepList,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setStatus(`Added "${data.title}" to your recipes.`);
        setTitle("");
        setIngredients("");
        setSteps("");
      })
      .catch(() => setStatus("Something went wrong — is the server running?"));
  }

  const labelClass = "block font-serif text-[#3A322A] mt-5 mb-1";
  const fieldClass = "w-full rounded-lg border border-[#E4DAcc] bg-white px-4 py-2.5 text-[#3A322A] outline-none focus:border-[#3F6B3F]";

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="font-serif text-3xl text-[#3A322A] mb-1">Add a recipe</h1>
      <p className="text-[#8A7E70] mb-2">Save your own — it'll show up in pantry matches.</p>

      <label className={labelClass}>Title</label>
      <input value={title} onChange={(e) => setTitle(e.target.value)} className={fieldClass} />

      <label className={labelClass}>Ingredients <span className="text-[#8A7E70] font-sans text-sm">(one per line)</span></label>
      <textarea value={ingredients} onChange={(e) => setIngredients(e.target.value)} rows={6} className={fieldClass} />

      <label className={labelClass}>Steps <span className="text-[#8A7E70] font-sans text-sm">(one per line)</span></label>
      <textarea value={steps} onChange={(e) => setSteps(e.target.value)} rows={6} className={fieldClass} />

      <button
        onClick={submitRecipe}
        className="mt-5 rounded-lg bg-[#3F6B3F] px-5 py-2.5 text-white hover:bg-[#2F512F]"
      >
        Add recipe
      </button>

      {status && <p className="mt-5 text-[#3F6B3F]">{status}</p>}
    </main>
  );
}