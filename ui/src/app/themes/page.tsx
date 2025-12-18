"use client";

import { useState } from "react";

// Sample content for mockups
const sampleMessages = [
  { role: "user", content: "Can you create a contact card for James Sadler?" },
  { role: "assistant", content: "I'll create a professional HTML contact card for James Sadler and save it to the Reports folder. The card will include his contact information, case details, and key contacts." },
];

const sampleFiles = [
  { name: "Database", type: "folder" },
  { name: "Reports", type: "folder" },
  { name: "Projects", type: "folder" },
  { name: "case_summary.md", type: "file" },
  { name: "contact_card.html", type: "file" },
];

// Theme A: Professional Legal
function ThemeA() {
  return (
    <div 
      className="rounded-xl overflow-hidden shadow-xl"
      style={{ 
        fontFamily: "'Georgia', serif",
        background: "#f8f7f4",
        border: "1px solid #d4c5a9"
      }}
    >
      {/* Header */}
      <div style={{ 
        background: "linear-gradient(135deg, #1e3a5f 0%, #2c4a6e 100%)",
        padding: "16px 20px",
        borderBottom: "3px solid #c9a227"
      }}>
        <h3 style={{ color: "#fff", fontSize: "16px", fontWeight: 600, margin: 0 }}>
          Roscoe AI Paralegal
        </h3>
        <p style={{ color: "#c9a227", fontSize: "11px", marginTop: "4px", fontStyle: "italic" }}>
          Legal Assistant
        </p>
      </div>

      {/* Chat Area */}
      <div style={{ padding: "16px", minHeight: "200px", background: "#fff" }}>
        {/* User Message */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "12px" }}>
          <div style={{
            background: "#1e3a5f",
            color: "#fff",
            padding: "10px 14px",
            borderRadius: "12px 12px 4px 12px",
            maxWidth: "80%",
            fontSize: "13px"
          }}>
            {sampleMessages[0].content}
          </div>
        </div>
        
        {/* Assistant Message */}
        <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "12px" }}>
          <div style={{
            background: "#f5f3ed",
            border: "1px solid #d4c5a9",
            color: "#2c3e50",
            padding: "10px 14px",
            borderRadius: "12px 12px 12px 4px",
            maxWidth: "80%",
            fontSize: "13px"
          }}>
            {sampleMessages[1].content}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div style={{ 
        padding: "12px 16px", 
        borderTop: "1px solid #d4c5a9",
        background: "#f8f7f4"
      }}>
        <div style={{
          display: "flex",
          gap: "8px",
          alignItems: "center"
        }}>
          <input 
            placeholder="Type a message..."
            style={{
              flex: 1,
              padding: "10px 14px",
              border: "1px solid #c9a227",
              borderRadius: "8px",
              background: "#fff",
              fontSize: "13px"
            }}
          />
          <button style={{
            background: "#c9a227",
            color: "#1e3a5f",
            padding: "10px 20px",
            borderRadius: "8px",
            border: "none",
            fontWeight: 600,
            cursor: "pointer"
          }}>
            Send
          </button>
        </div>
      </div>

      {/* File Browser Preview */}
      <div style={{ 
        padding: "12px 16px", 
        borderTop: "1px solid #d4c5a9",
        background: "#f8f7f4"
      }}>
        <div style={{ fontSize: "11px", color: "#6b7280", marginBottom: "8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>
          Files
        </div>
        {sampleFiles.slice(0, 3).map((file, i) => (
          <div key={i} style={{
            padding: "6px 8px",
            fontSize: "12px",
            color: "#1e3a5f",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            borderBottom: i < 2 ? "1px solid #e5e1d8" : "none"
          }}>
            <span>{file.type === "folder" ? "📁" : "📄"}</span>
            {file.name}
          </div>
        ))}
      </div>
    </div>
  );
}

// Theme B: Modern Minimal
function ThemeB() {
  return (
    <div 
      className="rounded-xl overflow-hidden"
      style={{ 
        fontFamily: "'Inter', -apple-system, sans-serif",
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
      }}
    >
      {/* Header */}
      <div style={{ 
        padding: "20px 24px",
        borderBottom: "1px solid #e5e7eb"
      }}>
        <h3 style={{ color: "#111827", fontSize: "15px", fontWeight: 600, margin: 0 }}>
          Roscoe AI Paralegal
        </h3>
      </div>

      {/* Chat Area */}
      <div style={{ padding: "20px 24px", minHeight: "200px", background: "#fafafa" }}>
        {/* User Message */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "16px" }}>
          <div style={{
            background: "#4f46e5",
            color: "#fff",
            padding: "12px 16px",
            borderRadius: "16px 16px 4px 16px",
            maxWidth: "80%",
            fontSize: "14px"
          }}>
            {sampleMessages[0].content}
          </div>
        </div>
        
        {/* Assistant Message */}
        <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "16px" }}>
          <div style={{
            background: "#ffffff",
            border: "1px solid #e5e7eb",
            color: "#374151",
            padding: "12px 16px",
            borderRadius: "16px 16px 16px 4px",
            maxWidth: "80%",
            fontSize: "14px"
          }}>
            {sampleMessages[1].content}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div style={{ 
        padding: "16px 24px", 
        borderTop: "1px solid #e5e7eb",
        background: "#fff"
      }}>
        <div style={{
          display: "flex",
          gap: "12px",
          alignItems: "center"
        }}>
          <input 
            placeholder="Type a message..."
            style={{
              flex: 1,
              padding: "12px 16px",
              border: "1px solid #e5e7eb",
              borderRadius: "12px",
              background: "#fafafa",
              fontSize: "14px"
            }}
          />
          <button style={{
            background: "#4f46e5",
            color: "#fff",
            padding: "12px 24px",
            borderRadius: "12px",
            border: "none",
            fontWeight: 500,
            cursor: "pointer"
          }}>
            Send
          </button>
        </div>
      </div>

      {/* File Browser Preview */}
      <div style={{ 
        padding: "16px 24px", 
        borderTop: "1px solid #e5e7eb",
        background: "#fff"
      }}>
        <div style={{ fontSize: "12px", color: "#6b7280", marginBottom: "12px", fontWeight: 500 }}>
          Files
        </div>
        {sampleFiles.slice(0, 3).map((file, i) => (
          <div key={i} style={{
            padding: "8px 12px",
            fontSize: "13px",
            color: "#374151",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            borderRadius: "8px",
            marginBottom: "4px",
            background: i === 0 ? "#f3f4f6" : "transparent"
          }}>
            <span style={{ opacity: 0.7 }}>{file.type === "folder" ? "📁" : "📄"}</span>
            {file.name}
          </div>
        ))}
      </div>
    </div>
  );
}

// Theme C: Gradient Modern
function ThemeC() {
  return (
    <div 
      className="rounded-2xl overflow-hidden"
      style={{ 
        fontFamily: "'Inter', -apple-system, sans-serif",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        boxShadow: "0 20px 40px rgba(102, 126, 234, 0.3)"
      }}
    >
      {/* Header */}
      <div style={{ 
        padding: "20px 24px",
        background: "rgba(255,255,255,0.1)",
        backdropFilter: "blur(10px)"
      }}>
        <h3 style={{ color: "#fff", fontSize: "16px", fontWeight: 600, margin: 0 }}>
          Roscoe AI Paralegal
        </h3>
        <p style={{ color: "rgba(255,255,255,0.7)", fontSize: "12px", marginTop: "2px" }}>
          Your intelligent legal assistant
        </p>
      </div>

      {/* Chat Area */}
      <div style={{ padding: "20px", minHeight: "200px", background: "rgba(255,255,255,0.95)" }}>
        {/* User Message */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "16px" }}>
          <div style={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "#fff",
            padding: "12px 18px",
            borderRadius: "20px 20px 6px 20px",
            maxWidth: "80%",
            fontSize: "14px",
            boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)"
          }}>
            {sampleMessages[0].content}
          </div>
        </div>
        
        {/* Assistant Message */}
        <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "16px" }}>
          <div style={{
            background: "#fff",
            color: "#4a5568",
            padding: "12px 18px",
            borderRadius: "20px 20px 20px 6px",
            maxWidth: "80%",
            fontSize: "14px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            border: "1px solid rgba(102, 126, 234, 0.1)"
          }}>
            {sampleMessages[1].content}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div style={{ 
        padding: "16px 20px", 
        background: "#fff"
      }}>
        <div style={{
          display: "flex",
          gap: "12px",
          alignItems: "center"
        }}>
          <input 
            placeholder="Type a message..."
            style={{
              flex: 1,
              padding: "14px 20px",
              border: "2px solid #e9ecef",
              borderRadius: "25px",
              background: "#f8f9fa",
              fontSize: "14px"
            }}
          />
          <button style={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "#fff",
            padding: "14px 28px",
            borderRadius: "25px",
            border: "none",
            fontWeight: 600,
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(102, 126, 234, 0.4)"
          }}>
            Send
          </button>
        </div>
      </div>

      {/* File Browser Preview */}
      <div style={{ 
        padding: "16px 20px", 
        background: "#fff",
        borderTop: "1px solid #f0f0f0"
      }}>
        <div style={{ fontSize: "12px", color: "#764ba2", marginBottom: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
          Files
        </div>
        {sampleFiles.slice(0, 3).map((file, i) => (
          <div key={i} style={{
            padding: "10px 14px",
            fontSize: "13px",
            color: "#4a5568",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            borderRadius: "12px",
            marginBottom: "6px",
            background: i === 0 ? "linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)" : "#f8f9fa",
            border: i === 0 ? "1px solid rgba(102, 126, 234, 0.2)" : "1px solid transparent"
          }}>
            <span>{file.type === "folder" ? "📁" : "📄"}</span>
            {file.name}
          </div>
        ))}
      </div>
    </div>
  );
}

// Theme D: Dark Mode Professional
function ThemeD() {
  return (
    <div 
      className="rounded-xl overflow-hidden"
      style={{ 
        fontFamily: "'Inter', -apple-system, sans-serif",
        background: "#0f172a",
        border: "1px solid #1e293b",
        boxShadow: "0 20px 40px rgba(0,0,0,0.4)"
      }}
    >
      {/* Header */}
      <div style={{ 
        padding: "18px 20px",
        borderBottom: "1px solid #1e293b",
        background: "linear-gradient(180deg, #1e293b 0%, #0f172a 100%)"
      }}>
        <h3 style={{ color: "#f1f5f9", fontSize: "15px", fontWeight: 600, margin: 0, display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ 
            width: "8px", 
            height: "8px", 
            borderRadius: "50%", 
            background: "#10b981",
            boxShadow: "0 0 8px #10b981"
          }}></span>
          Roscoe AI Paralegal
        </h3>
      </div>

      {/* Chat Area */}
      <div style={{ padding: "20px", minHeight: "200px", background: "#0f172a" }}>
        {/* User Message */}
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "16px" }}>
          <div style={{
            background: "#1e293b",
            color: "#e2e8f0",
            padding: "12px 16px",
            borderRadius: "14px 14px 4px 14px",
            maxWidth: "80%",
            fontSize: "13px",
            border: "1px solid #334155"
          }}>
            {sampleMessages[0].content}
          </div>
        </div>
        
        {/* Assistant Message */}
        <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "16px" }}>
          <div style={{
            background: "linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%)",
            color: "#e2e8f0",
            padding: "12px 16px",
            borderRadius: "14px 14px 14px 4px",
            maxWidth: "80%",
            fontSize: "13px",
            border: "1px solid rgba(16, 185, 129, 0.3)"
          }}>
            {sampleMessages[1].content}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div style={{ 
        padding: "16px 20px", 
        borderTop: "1px solid #1e293b",
        background: "#0f172a"
      }}>
        <div style={{
          display: "flex",
          gap: "12px",
          alignItems: "center"
        }}>
          <input 
            placeholder="Type a message..."
            style={{
              flex: 1,
              padding: "12px 16px",
              border: "1px solid #334155",
              borderRadius: "10px",
              background: "#1e293b",
              fontSize: "13px",
              color: "#e2e8f0"
            }}
          />
          <button style={{
            background: "linear-gradient(135deg, #10b981 0%, #06b6d4 100%)",
            color: "#0f172a",
            padding: "12px 24px",
            borderRadius: "10px",
            border: "none",
            fontWeight: 600,
            cursor: "pointer",
            boxShadow: "0 0 20px rgba(16, 185, 129, 0.3)"
          }}>
            Send
          </button>
        </div>
      </div>

      {/* File Browser Preview */}
      <div style={{ 
        padding: "16px 20px", 
        borderTop: "1px solid #1e293b",
        background: "#0f172a"
      }}>
        <div style={{ fontSize: "11px", color: "#64748b", marginBottom: "12px", fontWeight: 500, textTransform: "uppercase", letterSpacing: "1px" }}>
          Files
        </div>
        {sampleFiles.slice(0, 3).map((file, i) => (
          <div key={i} style={{
            padding: "8px 12px",
            fontSize: "13px",
            color: "#cbd5e1",
            display: "flex",
            alignItems: "center",
            gap: "10px",
            borderRadius: "8px",
            marginBottom: "4px",
            background: i === 0 ? "#1e293b" : "transparent",
            border: i === 0 ? "1px solid #334155" : "1px solid transparent"
          }}>
            <span style={{ opacity: 0.8 }}>{file.type === "folder" ? "📁" : "📄"}</span>
            {file.name}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ThemesPage() {
  const [selected, setSelected] = useState<string | null>(null);

  const themes = [
    { id: "A", name: "Professional Legal", description: "Navy blue, gold accents, traditional law-firm aesthetic", component: ThemeA },
    { id: "B", name: "Modern Minimal", description: "Clean whites, indigo accent, generous whitespace", component: ThemeB },
    { id: "C", name: "Gradient Modern", description: "Purple-blue gradients, soft shadows, contemporary SaaS feel", component: ThemeC },
    { id: "D", name: "Dark Mode Professional", description: "Dark slate, cyan/emerald accents, power-user aesthetic", component: ThemeD },
  ];

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Choose Your Theme
          </h1>
          <p className="text-gray-600">
            Click on a theme to select it. You can also mix elements from different themes.
          </p>
        </div>

        {/* Theme Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {themes.map(({ id, name, description, component: Component }) => (
            <div 
              key={id}
              onClick={() => setSelected(id)}
              className={`cursor-pointer transition-all duration-200 ${
                selected === id 
                  ? "ring-4 ring-blue-500 ring-offset-4 rounded-2xl scale-[1.02]" 
                  : "hover:scale-[1.01]"
              }`}
            >
              {/* Theme Label */}
              <div className="flex items-center gap-3 mb-3">
                <span className={`
                  w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                  ${selected === id ? "bg-blue-500 text-white" : "bg-gray-300 text-gray-700"}
                `}>
                  {id}
                </span>
                <div>
                  <h2 className="font-semibold text-gray-900">{name}</h2>
                  <p className="text-sm text-gray-500">{description}</p>
                </div>
              </div>

              {/* Theme Preview */}
              <Component />
            </div>
          ))}
        </div>

        {/* Selection Status */}
        {selected && (
          <div className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-blue-600 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-3">
            <span>Theme {selected} selected!</span>
            <button 
              onClick={() => setSelected(null)}
              className="bg-white/20 hover:bg-white/30 px-3 py-1 rounded-full text-sm"
            >
              Clear
            </button>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-12 text-center text-gray-600">
          <p className="mb-2">
            <strong>Instructions:</strong> Review each theme above and decide which one you like best.
          </p>
          <p>
            Let me know which theme (A, B, C, or D) you prefer, or if you want to mix elements from multiple themes.
          </p>
        </div>
      </div>
    </div>
  );
}
