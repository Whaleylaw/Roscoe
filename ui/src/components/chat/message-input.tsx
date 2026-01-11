"use client";

import { useState, useRef } from "react";
import { Send, Paperclip, X } from "lucide-react";

export interface FileAttachment {
  name: string;
  size: number;
  type: string;
  data: string; // base64
}

interface MessageInputProps {
  onSend: (message: string, attachments?: FileAttachment[]) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [input, setInput] = useState("");
  const [attachments, setAttachments] = useState<FileAttachment[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const newAttachments: FileAttachment[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // Convert file to base64
      const reader = new FileReader();
      await new Promise<void>((resolve) => {
        reader.onload = () => {
          const base64 = reader.result as string;
          // Remove data URL prefix (e.g., "data:image/png;base64,")
          const base64Data = base64.split(',')[1] || base64;

          newAttachments.push({
            name: file.name,
            size: file.size,
            type: file.type,
            data: base64Data,
          });
          resolve();
        };
        reader.readAsDataURL(file);
      });
    }

    setAttachments(prev => [...prev, ...newAttachments]);

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((input.trim() || attachments.length > 0) && !disabled) {
      onSend(input.trim(), attachments.length > 0 ? attachments : undefined);
      setInput("");
      setAttachments([]);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 p-4 border-t border-[#d4c5a9] bg-[#f8f7f4]">
      {/* File attachments preview */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {attachments.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 bg-white border border-[#d4c5a9] rounded-lg px-3 py-1.5 text-xs"
            >
              <span className="text-[#2c3e50] font-medium truncate max-w-[150px]">
                {file.name}
              </span>
              <span className="text-[#8b7355]">
                ({(file.size / 1024).toFixed(1)}KB)
              </span>
              <button
                type="button"
                onClick={() => removeAttachment(index)}
                className="text-[#8b7355] hover:text-red-600 transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input row */}
      <div className="flex gap-3">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept="*/*"
        />

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="self-end p-2.5 text-[#1e3a5f] hover:bg-white/50 rounded-lg transition-colors disabled:opacity-50"
          title="Attach files"
        >
          <Paperclip className="h-5 w-5" />
        </button>

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 resize-none rounded-lg border border-[#c9a227] bg-white p-3 text-[13px] text-[#2c3e50] placeholder:text-[#8b7355] focus:outline-none focus:ring-2 focus:ring-[#c9a227]/50 focus:border-[#c9a227]"
          rows={2}
          disabled={disabled}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          disabled={disabled || (!input.trim() && attachments.length === 0)}
          className="self-end px-5 py-2.5 bg-[#c9a227] hover:bg-[#b8922a] text-[#1e3a5f] rounded-lg font-semibold text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
        >
          <Send className="h-4 w-4" />
          <span>Send</span>
        </button>
      </div>
    </form>
  );
}
