"use client"

import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Highlight from "@tiptap/extension-highlight"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Bold, Italic, Heading2, List, ListOrdered, Undo2, Redo2, Minus } from "lucide-react"
import { useState } from "react"

export interface AnalysisIssue {
  id: string
  type: "logic_contradiction" | "logic_gap" | "weak_evidence" | "clarity_issue"
  startPos: number
  endPos: number
  suggestion?: string
  message: string
  text?: string
}

interface RichTextEditorProps {
  onContentChange?: (content: string) => void
  initialContent?: string
  analysisActive?: boolean
  analysisIssues?: AnalysisIssue[]
  onSuggestionAccept?: (issueId: string) => void
}

const issueTypeColors: Record<string, string> = {
  logic_contradiction: "bg-red-100 text-red-700 border-red-300",
  logic_gap: "bg-orange-100 text-orange-700 border-orange-300",
  weak_evidence: "bg-yellow-100 text-yellow-700 border-yellow-300",
  clarity_issue: "bg-blue-100 text-blue-700 border-blue-300",
}

const issueTypeLabels: Record<string, string> = {
  logic_contradiction: "Logic Contradiction",
  logic_gap: "Logic Gap",
  weak_evidence: "Weak Evidence",
  clarity_issue: "Clarity Issue",
}

export function RichTextEditor({ 
  onContentChange, 
  initialContent, 
  analysisActive = false,
  analysisIssues = [],
  onSuggestionAccept
}: RichTextEditorProps) {
  const [hoveredIssueId, setHoveredIssueId] = useState<string | null>(null)
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null)

  const editor = useEditor({
    extensions: [
      StarterKit,
      Highlight.configure({ multicolor: true })
    ],
    content: initialContent || "<p>Start typing your content here...</p>",
    immediatelyRender: false,
    onUpdate: ({ editor }) => {
      onContentChange?.(editor.getHTML())
    },
    editable: !analysisActive,
  })

  if (!editor) {
    return null
  }

  const handleIssueClick = (issue: AnalysisIssue) => {
    if (!issue.suggestion || !issue.text) return

    const currentContent = editor.getHTML()
    const textToReplace = issue.text
    const replacement = issue.suggestion
    
    const newContent = currentContent.replace(
      new RegExp(textToReplace.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
      `<span class="bg-green-100 text-green-700 font-semibold animate-pulse">${replacement}</span>`
    )
    
    editor.commands.setContent(newContent)
    onContentChange?.(newContent)

    setTimeout(() => {
      const finalContent = currentContent.replace(
        new RegExp(textToReplace.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'),
        replacement
      )
      editor.commands.setContent(finalContent)
      onContentChange?.(finalContent)
      onSuggestionAccept?.(issue.id)
    }, 800)
  }

  const renderContentWithHighlights = () => {
    if (!analysisActive || analysisIssues.length === 0) {
      return null
    }

    let html = editor.getHTML()
    const sortedIssues = [...analysisIssues].sort((a, b) => b.endPos - a.endPos)

    sortedIssues.forEach((issue) => {
      const text = issue.text || "error"
      const escapedText = text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const regex = new RegExp(`(${escapedText})`, "g")
      
      html = html.replace(
        regex,
        `<span class="underline decoration-red-500 decoration-2 bg-red-100 cursor-pointer hover:bg-red-200 transition-all relative group px-0.5 rounded issue-highlight" data-issue-id="${issue.id}" data-issue-type="${issueTypeLabels[issue.type]}">${text}<span class="invisible group-hover:visible absolute bottom-full left-0 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap z-50 pointer-events-none">${issueTypeLabels[issue.type]}</span></span>`
      )
    })

    return html
  }

  return (
    <Card className="border-[rgba(55,50,47,0.12)] min-h-[600px] relative">
      <CardHeader className="border-b border-[rgba(55,50,47,0.12)]">
        <div className="flex items-center justify-between mb-4">
          <CardTitle className="text-lg">Document Editor</CardTitle>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleBold().run()}
            disabled={!editor.can().chain().focus().toggleBold().run() || analysisActive}
          >
            <Bold className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleItalic().run()}
            disabled={!editor.can().chain().focus().toggleItalic().run() || analysisActive}
          >
            <Italic className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            disabled={analysisActive}
          >
            <Heading2 className="h-4 w-4" />
          </Button>
          <div className="w-px bg-[rgba(55,50,47,0.12)]" />
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            disabled={analysisActive}
          >
            <List className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            disabled={analysisActive}
          >
            <ListOrdered className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().setHorizontalRule().run()}
            disabled={analysisActive}
          >
            <Minus className="h-4 w-4" />
          </Button>
          <div className="w-px bg-[rgba(55,50,47,0.12)]" />
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().undo().run()}
            disabled={!editor.can().chain().focus().undo().run() || analysisActive}
          >
            <Undo2 className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().redo().run()}
            disabled={!editor.can().chain().focus().redo().run() || analysisActive}
          >
            <Redo2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div 
          className={`min-h-[500px] p-4 rounded border focus-within:ring-2 ${
            analysisActive 
              ? 'bg-amber-50 border-amber-200 focus-within:ring-amber-300' 
              : 'bg-white border-[rgba(55,50,47,0.12)] focus-within:ring-[#37322F]/20'
          }`}
          onClick={(e) => {
            const target = e.target as HTMLElement
            if (target.classList.contains('issue-highlight')) {
              const issueId = target.getAttribute('data-issue-id')
              if (issueId) {
                const issue = analysisIssues.find(i => i.id === issueId)
                if (issue) {
                  handleIssueClick(issue)
                }
              }
            }
          }}
        >
          {analysisActive && analysisIssues.length > 0 ? (
            <div 
              className="prose prose-sm max-w-none text-[#37322F]"
              dangerouslySetInnerHTML={{ __html: renderContentWithHighlights() || editor.getHTML() }}
            />
          ) : (
            <EditorContent editor={editor} className="prose prose-sm max-w-none" />
          )}
        </div>
      </CardContent>
    </Card>
  )
}
