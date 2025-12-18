"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Highlight from "@tiptap/extension-highlight";
import TextStyle from "@tiptap/extension-text-style";
import Color from "@tiptap/extension-color";
import { Button } from "@/components/ui/button";
import {
  Bold,
  Italic,
  Strikethrough as StrikethroughIcon,
  List,
  ListOrdered,
  Heading1,
  Heading2,
  Undo,
  Redo,
  Save,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface DocumentEditorProps {
  initialContent: string;
  onSave: (content: string) => void;
  path: string;
}

export function DocumentEditor({ initialContent, onSave, path }: DocumentEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Highlight.configure({ multicolor: true }),
      TextStyle,
      Color,
    ],
    content: initialContent,
    editorProps: {
      attributes: {
        class: "prose prose-sm max-w-none p-6 focus:outline-none min-h-[500px]",
      },
    },
  });

  const handleSave = () => {
    if (!editor) return;
    const html = editor.getHTML();
    onSave(html);
  };

  if (!editor) {
    return <div>Loading editor...</div>;
  }

  return (
    <div className="flex h-full flex-col">
      {/* Toolbar */}
      <div className="flex items-center gap-1 border-b p-2 flex-wrap">
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive("bold") ? "bg-accent" : ""}
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive("italic") ? "bg-accent" : ""}
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={editor.isActive("strike") ? "bg-accent" : ""}
        >
          <StrikethroughIcon className="h-4 w-4" />
        </Button>

        <div className="w-px h-6 bg-border mx-1" />

        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={editor.isActive("heading", { level: 1 }) ? "bg-accent" : ""}
        >
          <Heading1 className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={editor.isActive("heading", { level: 2 }) ? "bg-accent" : ""}
        >
          <Heading2 className="h-4 w-4" />
        </Button>

        <div className="w-px h-6 bg-border mx-1" />

        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive("bulletList") ? "bg-accent" : ""}
        >
          <List className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive("orderedList") ? "bg-accent" : ""}
        >
          <ListOrdered className="h-4 w-4" />
        </Button>

        <div className="flex-1" />

        <Button size="sm" variant="ghost" onClick={() => editor.chain().focus().undo().run()}>
          <Undo className="h-4 w-4" />
        </Button>
        <Button size="sm" variant="ghost" onClick={() => editor.chain().focus().redo().run()}>
          <Redo className="h-4 w-4" />
        </Button>

        <Button size="sm" variant="default" onClick={handleSave}>
          <Save className="h-4 w-4 mr-1" />
          Save
        </Button>
      </div>

      {/* Editor */}
      <ScrollArea className="flex-1">
        <EditorContent editor={editor} className="h-full" />
      </ScrollArea>
    </div>
  );
}
