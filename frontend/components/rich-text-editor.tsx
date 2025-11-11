"use client"

import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bold, Italic, Heading2, List, ListOrdered, Undo2, Redo2, Minus } from "lucide-react"

interface RichTextEditorProps {
  onContentChange?: (content: string) => void
  initialContent?: string
}

export function RichTextEditor({ onContentChange, initialContent }: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: initialContent || "<p>Start typing your content here...</p>",
    immediatelyRender: false,
    onUpdate: ({ editor }) => {
      onContentChange?.(editor.getHTML())
    },
  })

  if (!editor) {
    return null
  }

  return (
    <Card className="border-[rgba(55,50,47,0.12)] min-h-[600px]">
      <CardHeader className="border-b border-[rgba(55,50,47,0.12)]">
        <CardTitle className="text-lg">Document Editor</CardTitle>
        <div className="flex flex-wrap gap-2 mt-4">
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleBold().run()}
            disabled={!editor.can().chain().focus().toggleBold().run()}
          >
            <Bold className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleItalic().run()}
            disabled={!editor.can().chain().focus().toggleItalic().run()}
          >
            <Italic className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          >
            <Heading2 className="h-4 w-4" />
          </Button>
          <div className="w-px bg-[rgba(55,50,47,0.12)]" />
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
          >
            <ListOrdered className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().setHorizontalRule().run()}
          >
            <Minus className="h-4 w-4" />
          </Button>
          <div className="w-px bg-[rgba(55,50,47,0.12)]" />
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().chain().focus().undo().run()}
          >
            <Undo2 className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().chain().focus().redo().run()}
          >
            <Redo2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="min-h-[500px] p-4 bg-white rounded border border-[rgba(55,50,47,0.12)] focus-within:ring-2 focus-within:ring-[#37322F]/20">
          <EditorContent editor={editor} className="prose prose-sm max-w-none" />
        </div>
      </CardContent>
    </Card>
  )
}
