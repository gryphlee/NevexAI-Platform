"use client";

import { useEffect, useState } from "react";

export default function ResourcesPage() {
  const [resources, setResources] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState("");

  const loadResources = async () => {
    setIsLoading(true);
    setSaveStatus("");
    try {
      const response = await fetch("http://127.0.0.1:8000/resources");
      if (!response.ok) throw new Error("Failed to fetch resources");
      const data = await response.json();
      setResources(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadResources(); }, []);

  const handleAdd = () => {
    setResources((prev) => [
      ...prev,
      { title: "", link: "", type: "", tags: [] },
    ]);
  };

  const handleChange = (index, field, value) => {
    setResources((prev) => prev.map((r, i) => i === index ? { ...r, [field]: value } : r));
  };

  const handleTagChange = (index, value) => {
    const tags = value.split(",").map(t => t.trim()).filter(Boolean);
    setResources((prev) => prev.map((r, i) => i === index ? { ...r, tags } : r));
  };

  const handleRemove = (index) => {
    setResources((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSave = async () => {
    setSaveStatus("");
    try {
      const response = await fetch("http://127.0.0.1:8000/resources", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(resources),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Failed to save resources");
      setSaveStatus("Saved successfully.");
    } catch (err) {
      setSaveStatus(`Error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Resource Manager</h2>

      <div className="bg-gray-900/50 border border-cyan-400/20 rounded-xl p-6">
        {isLoading && <p className="text-gray-400">Loading resources...</p>}
        {error && <p className="text-red-500">Error: {error}</p>}

        {!isLoading && !error && (
          <>
            <div className="flex items-center justify-between mb-4">
              <button
                className="px-3 py-2 rounded bg-cyan-600 hover:bg-cyan-700 text-white text-sm"
                onClick={handleAdd}
                type="button"
              >
                Add Resource
              </button>
              <button
                className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm"
                onClick={handleSave}
                type="button"
              >
                Save Changes
              </button>
            </div>

            <div className="space-y-4">
              {resources.length === 0 && (
                <p className="text-gray-400">No resources yet. Click "Add Resource" to create one.</p>
              )}

              {resources.map((res, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-gray-800/40 p-4 rounded-lg border border-gray-700">
                  <label htmlFor={`res-title-${index}`} className="sr-only">Title</label>
                  <input
                    id={`res-title-${index}`}
                    name={`res-title-${index}`}
                    className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                    placeholder="Title"
                    value={res.title}
                    onChange={(e) => handleChange(index, "title", e.target.value)}
                  />
                  <label htmlFor={`res-link-${index}`} className="sr-only">Link</label>
                  <input
                    id={`res-link-${index}`}
                    name={`res-link-${index}`}
                    className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                    placeholder="Link"
                    value={res.link}
                    onChange={(e) => handleChange(index, "link", e.target.value)}
                  />
                  <label htmlFor={`res-type-${index}`} className="sr-only">Type</label>
                  <input
                    id={`res-type-${index}`}
                    name={`res-type-${index}`}
                    className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                    placeholder="Type (e.g., video, doc)"
                    value={res.type}
                    onChange={(e) => handleChange(index, "type", e.target.value)}
                  />
                  <label htmlFor={`res-tags-${index}`} className="sr-only">Tags</label>
                  <input
                    id={`res-tags-${index}`}
                    name={`res-tags-${index}`}
                    className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                    placeholder="Tags (comma-separated)"
                    value={res.tags?.join(", ") || ""}
                    onChange={(e) => handleTagChange(index, e.target.value)}
                  />
                  <div className="md:col-span-4 flex justify-end">
                    <button
                      className="px-3 py-1 rounded bg-red-600 hover:bg-red-700 text-white text-xs"
                      onClick={() => handleRemove(index)}
                      type="button"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {saveStatus && (
              <p className={`text-sm mt-4 ${saveStatus.startsWith("Error") ? "text-red-500" : "text-green-500"}`}>{saveStatus}</p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
