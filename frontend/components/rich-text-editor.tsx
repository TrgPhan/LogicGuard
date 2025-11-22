"use client"

import { useEditor, EditorContent } from "@tiptap/react"
import type { ChainedCommands } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Highlight from "@tiptap/extension-highlight"
import Underline from "@tiptap/extension-underline"
import { TextStyle } from "@tiptap/extension-text-style"
import Color from "@tiptap/extension-color"
import FontFamily from "@tiptap/extension-font-family"
import Link from "@tiptap/extension-link"
import TaskList from "@tiptap/extension-task-list"
import TaskItem from "@tiptap/extension-task-item"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Bold,
  Italic,
  Undo2,
  Redo2,
  Underline as UnderlineIcon,
  Strikethrough,
  Link2,
  Highlighter,
  Palette,
  ChevronDown,
  List,
  ListOrdered,
  ListTodo,
  Type,
  Heading1,
  Heading2,
  Heading3,
  Minus,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { useEffect, useState } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface RichTextEditorProps {
  onContentChange?: (content: string) => void
  initialContent?: string
  analysisActive?: boolean
  analysisIssues?: AnalysisIssue[]
  onSuggestionAccept?: (issueId: string) => void
}

export type AnalysisIssue = {
  id: string
  type:
    | "logic_contradiction"
    | "logic_gap"
    | "weak_evidence"
    | "clarity_issue"
    | "undefined_term"
  startPos: number
  endPos: number
  text: string
  message: string
  suggestion?: string
}

const issueTypeLabels: Record<AnalysisIssue["type"], string> = {
  logic_contradiction: "Logic Contradiction",
  logic_gap: "Logic Gap",
  weak_evidence: "Weak Evidence",
  clarity_issue: "Clarity Issue",
  undefined_term: "Undefined Term",
}

export function RichTextEditor({
  onContentChange,
  initialContent,
  analysisActive = false,
  analysisIssues = [],
  onSuggestionAccept,
}: RichTextEditorProps) {
  const [replacedWords, setReplacedWords] = useState<Set<string>>(new Set())
  const [selectedBlock, setSelectedBlock] = useState("Text")
  const [selectedFont, setSelectedFont] = useState("Inter")
  const [selectedSize, setSelectedSize] = useState("Medium")
  const [fontColor, setFontColor] = useState("#37322F")

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Highlight.configure({ multicolor: true }),
      Underline,
      TextStyle,
      Color.configure({ types: ["textStyle"] }),
      FontFamily.configure({ types: ["textStyle"] }),
      Link.configure({ openOnClick: false, autolink: true, linkOnPaste: true }),
      TaskList.configure({ HTMLAttributes: { class: "not-prose" } }),
      TaskItem.configure({ nested: true }),
    ],
    content: initialContent || "<p>Start typing your content here...</p>",
    immediatelyRender: false,
    onUpdate: ({ editor }) => {
      onContentChange?.(editor.getHTML())
    },
    editable: !analysisActive,
  })

  const fontSizes: Record<string, string> = {
    Smaller: "0.875rem",
    Small: "0.9375rem",
    Medium: "1rem",
    Large: "1.125rem",
    "Extra Large": "1.25rem",
  }

  type FontSizeLabel = keyof typeof fontSizes

  useEffect(() => {
    if (!editor) return

    const syncToolbarState = () => {
      const nextBlockLabel = editor.isActive("heading", { level: 1 })
        ? "Heading 1"
        : editor.isActive("heading", { level: 2 })
          ? "Heading 2"
          : editor.isActive("heading", { level: 3 })
            ? "Heading 3"
            : editor.isActive("taskList")
              ? "Todo list"
            : editor.isActive("bulletList")
              ? "Bullet list"
              : editor.isActive("orderedList")
                ? "Numbered list"
                : "Text"

      setSelectedBlock(prev => (prev === nextBlockLabel ? prev : nextBlockLabel))

      const textStyleAttrs = editor.getAttributes("textStyle") as {
        fontFamily?: string
        fontSize?: string
        color?: string
      }

      const nextFont = textStyleAttrs.fontFamily || "Inter"
      setSelectedFont(prev => (prev === nextFont ? prev : nextFont))

      const fontSizeEntry = (Object.entries(fontSizes) as [FontSizeLabel, string][])
        .find(([, value]) => value === textStyleAttrs.fontSize)
      const nextSize = fontSizeEntry ? fontSizeEntry[0] : "Medium"
      setSelectedSize(prev => (prev === nextSize ? prev : nextSize))

      const nextColor = textStyleAttrs.color || "#37322F"
      setFontColor(prev => (prev === nextColor ? prev : nextColor))
    }

    editor.on("selectionUpdate", syncToolbarState)
    editor.on("transaction", syncToolbarState)
    syncToolbarState()

    return () => {
      editor.off("selectionUpdate", syncToolbarState)
      editor.off("transaction", syncToolbarState)
    }
  }, [editor, fontSizes])

  if (editor && !analysisActive && replacedWords.size > 0) {
    const currentContent = editor.getHTML()
    let cleanedContent = currentContent

    replacedWords.forEach(word => {
      cleanedContent = cleanedContent.replace(
        new RegExp(
          `<span class="bg-green-100 text-green-700 font-semibold animate-pulse">${word.replace(
            /[.*+?^${}()|[\]\\]/g,
            "\\$&",
          )}</span>`,
          "g",
        ),
        word,
      )
    })

    if (cleanedContent !== currentContent) {
      editor.commands.setContent(cleanedContent)
      onContentChange?.(cleanedContent)
    }
    setReplacedWords(new Set())
  }

  if (!editor) {
    return null
  }

  type ExtendedChain = ChainedCommands & {
    setFontFamily: (fontFamily: string) => ExtendedChain
    unsetFontFamily: () => ExtendedChain
    setTextStyle: (attributes: Record<string, string>) => ExtendedChain
    unsetTextStyle: () => ExtendedChain
    setColor: (color: string) => ExtendedChain
    toggleUnderline: () => ExtendedChain
    toggleTaskList: () => ExtendedChain
  }

  const focusChain = () => editor.chain().focus() as ExtendedChain

  const handleBlockSelect = (label: string, action: () => boolean) => {
    if (analysisActive) return
    const executed = action()
    if (executed) {
      setSelectedBlock(label)
    }
  }

  const handleFontFamilyChange = (family: string) => {
    if (analysisActive) return
    if (!family || family === "Inter") {
      focusChain().unsetFontFamily().run()
      setSelectedFont("Inter")
      return
    }

    focusChain().setFontFamily(family).run()
    setSelectedFont(family)
  }

  const handleFontSizeChange = (label: FontSizeLabel) => {
    if (analysisActive) return
    const value = fontSizes[label]
    focusChain().setTextStyle({ fontSize: value }).run()
    setSelectedSize(label)
  }

  const handleSetLink = () => {
    if (analysisActive) return
    const previousUrl = editor.getAttributes("link").href as string | undefined
    const url = window.prompt("Enter URL", previousUrl || "")
    if (url === null) return
    if (url === "") {
      editor.chain().focus().unsetLink().run()
      return
    }
    editor.chain().focus().extendMarkRange("link").setLink({ href: url }).run()
  }

  const renderBlockMenuItem = (label: string, Icon: LucideIcon, action: () => boolean) => (
    <DropdownMenuItem
      onClick={() => handleBlockSelect(label, action)}
      disabled={analysisActive}
      className={cn("flex items-center gap-2 text-sm", selectedBlock === label && "bg-muted")}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </DropdownMenuItem>
  )

  const handleColorChange = (value: string) => {
    if (analysisActive) return
    focusChain().setColor(value).run()
    setFontColor(value)
  }

  const handleIssueClick = (issue: AnalysisIssue) => {
    if (!issue.suggestion || !issue.text) return

    const currentContent = editor.getHTML()
    const escapedText = issue.text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    const newContent = currentContent.replace(
      new RegExp(escapedText, "g"),
      `<span class="bg-green-100 text-green-700 font-semibold animate-pulse">${issue.suggestion}</span>`,
    )

    editor.commands.setContent(newContent)
    onContentChange?.(newContent)

    const newReplacedWords = new Set(replacedWords)
    newReplacedWords.add(issue.suggestion)
    setReplacedWords(newReplacedWords)

    setTimeout(() => {
      if (!issue.text || !issue.suggestion) return
      const escapedTextInner = issue.text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
      const finalContent = currentContent.replace(new RegExp(escapedTextInner, "g"), issue.suggestion)
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

    sortedIssues.forEach(issue => {
      if (!issue.text) return

      const text = issue.text
      const escapedText = text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
      const regex = new RegExp(`(${escapedText})`, "g")

      const label = issueTypeLabels[issue.type] ?? "Issue"

      html = html.replace(
        regex,
        `<span class="underline decoration-red-500 decoration-2 bg-red-100 cursor-pointer hover:bg-red-200 transition-all relative group px-0.5 rounded issue-highlight" data-issue-id="${issue.id}" data-issue-type="${label}">${text}<span class="invisible group-hover:visible absolute bottom-full left-0 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap z-50 pointer-events-none">${label}</span></span>`,
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
        <div className="flex flex-wrap items-center gap-2">
          {/* Block type */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                className="h-9 bg-transparent min-w-[120px] justify-between"
                disabled={analysisActive}
              >
                <span className="text-sm font-medium">{selectedBlock}</span>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-60">
              <DropdownMenuLabel className="text-[11px] tracking-wide text-muted-foreground">
                HIERARCHY
              </DropdownMenuLabel>
              {renderBlockMenuItem("Text", Type, () => focusChain().setParagraph().run())}
              {renderBlockMenuItem("Heading 1", Heading1, () => focusChain().toggleHeading({ level: 1 }).run())}
              {renderBlockMenuItem("Heading 2", Heading2, () => focusChain().toggleHeading({ level: 2 }).run())}
              {renderBlockMenuItem("Heading 3", Heading3, () => focusChain().toggleHeading({ level: 3 }).run())}

              <DropdownMenuSeparator />
              <DropdownMenuLabel className="text-[11px] tracking-wide text-muted-foreground">
                LISTS
              </DropdownMenuLabel>
              {renderBlockMenuItem("Bullet list", List, () => focusChain().toggleBulletList().run())}
              {renderBlockMenuItem("Numbered list", ListOrdered, () => focusChain().toggleOrderedList().run())}
              {renderBlockMenuItem("Todo list", ListTodo, () => focusChain().toggleTaskList().run())}

              <DropdownMenuSeparator />
              <DropdownMenuLabel className="text-[11px] tracking-wide text-muted-foreground">
                INSERT
              </DropdownMenuLabel>
              <DropdownMenuItem
                disabled={analysisActive}
                onClick={() => {
                  if (analysisActive) return
                  focusChain().setHorizontalRule().run()
                }}
                className="flex items-center gap-2 text-sm"
              >
                <Minus className="h-4 w-4" />
                <span>Divider</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Font family */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                className="h-9 bg-transparent min-w-[120px] justify-between"
                disabled={analysisActive}
              >
                <span className="text-sm font-medium">{selectedFont}</span>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-40">
              <DropdownMenuLabel>Sans Serif</DropdownMenuLabel>
              {["Inter", "Arial", "Helvetica"].map(font => (
                <DropdownMenuItem key={font} onClick={() => handleFontFamilyChange(font)}>
                  {font}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuLabel>Serif</DropdownMenuLabel>
              {["Times New Roman", "Garamond", "Georgia"].map(font => (
                <DropdownMenuItem key={font} onClick={() => handleFontFamilyChange(font)}>
                  {font}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuLabel>Monospace</DropdownMenuLabel>
              {["Courier", "Courier New"].map(font => (
                <DropdownMenuItem key={font} onClick={() => handleFontFamilyChange(font)}>
                  {font}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Font size */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                className="h-9 bg-transparent min-w-[120px] justify-between"
                disabled={analysisActive}
              >
                <span className="text-sm font-medium">{selectedSize}</span>
                <ChevronDown className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-36">
              {Object.keys(fontSizes).map(size => (
                <DropdownMenuItem
                  key={size}
                  onClick={() => handleFontSizeChange(size as keyof typeof fontSizes)}
                >
                  {size}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          <div className="w-px bg-[rgba(55,50,47,0.12)]" />

          {/* Inline formatting */}
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
            onClick={() => focusChain().toggleUnderline().run()}
            disabled={analysisActive}
          >
            <UnderlineIcon className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleStrike().run()}
            disabled={analysisActive}
          >
            <Strikethrough className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={() => editor.chain().focus().toggleHighlight().run()}
            disabled={analysisActive}
          >
            <Highlighter className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-transparent"
            onClick={handleSetLink}
            disabled={analysisActive}
          >
            <Link2 className="h-4 w-4" />
          </Button>

          {/* Color picker */}
          <label
            className={cn(
              "relative h-9 w-9 cursor-pointer rounded-md border bg-white text-muted-foreground transition hover:bg-muted flex items-center justify-center",
              analysisActive && "pointer-events-none opacity-50",
            )}
          >
            <Palette className="h-4 w-4" />
            <input
              type="color"
              value={fontColor}
              onChange={event => handleColorChange(event.target.value)}
              className="absolute inset-0 opacity-0 cursor-pointer"
              disabled={analysisActive}
            />
          </label>

          {/* Undo / Redo */}
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
              ? "bg-amber-50 border-amber-200 focus-within:ring-amber-300"
              : "bg-white border-[rgba(55,50,47,0.12)] focus-within:ring-[#37322F]/20"
          }`}
          onClick={e => {
            const target = e.target as HTMLElement
            if (target.classList.contains("issue-highlight")) {
              const issueId = target.getAttribute("data-issue-id")
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
