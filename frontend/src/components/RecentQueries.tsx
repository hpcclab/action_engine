// components/RecentQueries.tsx
import React from "react";

const recent = [
  { query: "Resize an image to 800x600", time: "3h ago" },
  { query: "Convert an image to PDF", time: "Yesterday" },
];

export default function RecentQueries() {
  return (
    <div>
      <h2 className="text-lg font-semibold mb-3 text-gray-700">Recent Queries</h2>
      <div className="flex flex-wrap gap-4">
        {recent.map((item, i) => (
          <div
            key={i}
            className="px-4 py-2 bg-purple-100 text-purple-800 rounded-lg text-sm shadow-sm"
          >
            “{item.query}” <span className="text-xs text-gray-500 ml-2">{item.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
