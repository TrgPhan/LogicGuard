"use client"

import "@/styles/editor-override.css"
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
import { Extension } from "@tiptap/core"

// Custom FontSize extension
const FontSize = Extension.create({
  name: "fontSize",

  addOptions() {
    return {
      types: ["textStyle"],
    }
  },

  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          fontSize: {
            default: null,
            parseHTML: (element) => element.style.fontSize || null,
            renderHTML: (attributes) => {
              if (!attributes.fontSize) {
                return {}
              }
              return {
                style: `font-size: ${attributes.fontSize} !important`,
              }
            },
          },
        },
      },
    ]
  },
})
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
  Minus
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { useEffect, useState, useCallback, useRef } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

interface RichTextEditorProps {
  onContentChange?: (content: string) => void
  initialContent?: string
  analysisActive?: boolean
  analysisIssues?: AnalysisIssue[]
  onSuggestionAccept?: (issueId: string) => void
  onIssueClick?: (handleIssueClick: (issue: AnalysisIssue) => void) => void
}

export interface AnalysisIssue {
  id: string
  type: "logic_contradiction" | "logic_gap" | "weak_evidence" | "clarity_issue"
  startPos: number
  endPos: number
  suggestion?: string
  message: string
  text?: string
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
  onSuggestionAccept,
  onIssueClick
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
          levels: [1, 2, 3]
        }
      }),
      Highlight.configure({ multicolor: true }),
      Underline,
      TextStyle,
      Color.configure({ types: ["textStyle"] }),
      FontFamily.configure({ types: ["textStyle"] }),
      Link.configure({ openOnClick: false, autolink: true, linkOnPaste: true }),
      TaskList.configure({ HTMLAttributes: { class: "not-prose" } }),
      TaskItem.configure({ nested: true }),
      FontSize
    ],
    content: initialContent || "",
    immediatelyRender: false,
    onUpdate: ({ editor }) => {
      onContentChange?.(editor.getHTML())
    },
    editable: !analysisActive,
    editorProps: {
      attributes: {
        class: 'prose-editor',
        'data-placeholder': 'Start typing your content here...'
      }
    }
  })

  const fontSizes: Record<string, string> = {
    Smaller: "0.875rem",
    Small: "0.9375rem",
    Medium: "1rem",
    Large: "1.125rem",
    "Extra Large": "1.25rem"
  }

  type FontSizeLabel = keyof typeof fontSizes

  // Remove green highlights when analysis is turned off
  useEffect(() => {
    if (!editor) return
    
    if (!analysisActive) {
      // Remove all suggestion-applied highlights when analysis is turned off
      const currentContent = editor.getHTML()
      // Remove suggestion-applied spans but keep the text content
      // Handle both single and double quotes in class attribute
      let cleanedContent = currentContent.replace(
        /<span[^>]*class="[^"]*suggestion-applied[^"]*"[^>]*>(.*?)<\/span>/gi,
        '$1'
      )
      cleanedContent = cleanedContent.replace(
        /<span[^>]*class='[^']*suggestion-applied[^']*'[^>]*>(.*?)<\/span>/gi,
        '$1'
      )
      // Also remove suggestion-applying spans
      cleanedContent = cleanedContent.replace(
        /<span[^>]*class="[^"]*suggestion-applying[^"]*"[^>]*>(.*?)<\/span>/gi,
        '$1'
      )
      cleanedContent = cleanedContent.replace(
        /<span[^>]*class='[^']*suggestion-applying[^']*'[^>]*>(.*?)<\/span>/gi,
        '$1'
      )
      
      if (cleanedContent !== currentContent) {
        editor.commands.setContent(cleanedContent)
        onContentChange?.(cleanedContent)
      }
    }
  }, [analysisActive, editor, onContentChange])

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

      setSelectedBlock((prev) => (prev === nextBlockLabel ? prev : nextBlockLabel))

      const textStyleAttrs = editor.getAttributes("textStyle") as {
        fontFamily?: string
        fontSize?: string
        color?: string
      }

      const nextFont = textStyleAttrs.fontFamily || "Inter"
      setSelectedFont((prev) => (prev === nextFont ? prev : nextFont))

      const fontSizeEntry = (Object.entries(fontSizes) as [FontSizeLabel, string][])
        .find(([, value]) => value === textStyleAttrs.fontSize)
      const nextSize = fontSizeEntry ? fontSizeEntry[0] : "Medium"
      setSelectedSize((prev) => (prev === nextSize ? prev : nextSize))

      const nextColor = textStyleAttrs.color || "#37322F"
      setFontColor((prev) => (prev === nextColor ? prev : nextColor))
    }

    editor.on("selectionUpdate", syncToolbarState)
    editor.on("transaction", syncToolbarState)
    syncToolbarState()

    return () => {
      editor.off("selectionUpdate", syncToolbarState)
      editor.off("transaction", syncToolbarState)
    }
  }, [editor])

  type ExtendedChain = ChainedCommands & {
    setFontFamily: (fontFamily: string) => ExtendedChain
    unsetFontFamily: () => ExtendedChain
    setTextStyle: (attributes: Record<string, string>) => ExtendedChain
    unsetTextStyle: () => ExtendedChain
    setColor: (color: string) => ExtendedChain
    toggleUnderline: () => ExtendedChain
    toggleTaskList: () => ExtendedChain
  }

  const focusChain = () => editor?.chain().focus() as ExtendedChain | undefined

  const handleIssueClick = useCallback((issue: AnalysisIssue) => {
    if (!issue.suggestion || !issue.text || !editor) {
      console.log("[Editor] Cannot apply suggestion - missing data:", { 
        hasSuggestion: !!issue.suggestion, 
        hasText: !!issue.text, 
        hasEditor: !!editor 
      })
      return
    }

    console.log("[Editor] Applying suggestion:", { 
      text: issue.text, 
      suggestion: issue.suggestion 
    })

    const currentContent = editor.getHTML()
    console.log("[Editor] Current content length:", currentContent.length)
    
    const escapedText = issue.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    
    // First, remove any existing highlights to find the original text
    // This handles cases where text might already be highlighted with red (from analysis)
    let contentToSearch = currentContent
    // Remove red issue highlights
    contentToSearch = contentToSearch.replace(
      /<span[^>]*class="[^"]*issue-highlight[^"]*"[^>]*>(.*?)<\/span>/gi,
      '$1'
    )
    // Remove any existing green highlights
    contentToSearch = contentToSearch.replace(
      /<span[^>]*class="[^"]*suggestion-applied[^"]*"[^>]*>(.*?)<\/span>/gi,
      '$1'
    )
    contentToSearch = contentToSearch.replace(
      /<span[^>]*class='[^']*suggestion-applied[^']*'[^>]*>(.*?)<\/span>/gi,
      '$1'
    )
    
    // Check if text exists in content
    const textExists = contentToSearch.includes(issue.text)
    console.log("[Editor] Text exists in content:", textExists)
    
    if (!textExists) {
      console.warn("[Editor] Text not found in content:", issue.text)
      // Try case-insensitive search
      const textLower = issue.text.toLowerCase()
      const contentLower = contentToSearch.toLowerCase()
      if (contentLower.includes(textLower)) {
        // Find the actual text with original case
        const regex = new RegExp(escapedText, 'gi')
        const match = contentToSearch.match(regex)
        if (match && match[0]) {
          console.log("[Editor] Found text with different case:", match[0])
          // Use the matched text instead
          const matchedText = match[0]
          const escapedMatchedText = matchedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
          
          // First, show animated highlight - replace original text with suggestion
          const animatedContent = contentToSearch.replace(
            new RegExp(escapedMatchedText, 'g'),
            `<span class="suggestion-applying bg-green-200 text-green-800 font-semibold animate-pulse px-1 rounded">${issue.suggestion}</span>`
          )

          editor.commands.setContent(animatedContent)
          onContentChange?.(animatedContent)

          // After animation, apply permanent green highlight
          setTimeout(() => {
            if (!issue.suggestion) return
            
            const currentContentAfterAnimation = editor.getHTML()
            
            // Remove suggestion-applying spans first
            let cleanedContent = currentContentAfterAnimation.replace(
              /<span[^>]*class="[^"]*suggestion-applying[^"]*"[^>]*>(.*?)<\/span>/gi,
              '$1'
            )
            cleanedContent = cleanedContent.replace(
              /<span[^>]*class='[^']*suggestion-applying[^']*'[^>]*>(.*?)<\/span>/gi,
              '$1'
            )
            
            // Replace with highlighted suggestion
            const escapedSuggestion = issue.suggestion.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
            const finalContent = cleanedContent.replace(
              new RegExp(`(${escapedSuggestion})`, 'g'),
              `<span class="suggestion-applied bg-green-100 text-green-800 font-medium px-1 rounded">${issue.suggestion}</span>`
            )
            
            editor.commands.setContent(finalContent)
            onContentChange?.(finalContent)
            onSuggestionAccept?.(issue.id)
          }, 800)
          return
        }
      }
      console.error("[Editor] Text not found even with case-insensitive search")
      return
    }
    
    // First, show animated highlight - replace original text with suggestion
    const animatedContent = contentToSearch.replace(
      new RegExp(escapedText, 'g'),
      `<span class="suggestion-applying bg-green-200 text-green-800 font-semibold animate-pulse px-1 rounded">${issue.suggestion}</span>`
    )

    console.log("[Editor] Applied animated highlight")
    editor.commands.setContent(animatedContent)
    onContentChange?.(animatedContent)

    // After animation, apply permanent green highlight
    setTimeout(() => {
      if (!issue.text || !issue.suggestion) return
      
      // Get current content after animation
      const currentContentAfterAnimation = editor.getHTML()
      
      // Remove suggestion-applying spans first
      let cleanedContent = currentContentAfterAnimation.replace(
        /<span[^>]*class="[^"]*suggestion-applying[^"]*"[^>]*>(.*?)<\/span>/gi,
        '$1'
      )
      cleanedContent = cleanedContent.replace(
        /<span[^>]*class='[^']*suggestion-applying[^']*'[^>]*>(.*?)<\/span>/gi,
        '$1'
      )
      
      // Now replace the suggestion text (or original text if not replaced) with highlighted suggestion
      const escapedSuggestion = issue.suggestion.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const escapedOriginalText = issue.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      
      // Try to replace suggestion first (if already applied), then original text
      let finalContent = cleanedContent.replace(
        new RegExp(`(${escapedSuggestion})`, 'g'),
        `<span class="suggestion-applied bg-green-100 text-green-800 font-medium px-1 rounded">${issue.suggestion}</span>`
      )
      
      // If no replacement happened, try original text
      if (finalContent === cleanedContent) {
        finalContent = cleanedContent.replace(
          new RegExp(`(${escapedOriginalText})`, 'g'),
          `<span class="suggestion-applied bg-green-100 text-green-800 font-medium px-1 rounded">${issue.suggestion}</span>`
        )
      }
      
      console.log("[Editor] Applied permanent highlight")
      editor.commands.setContent(finalContent)
      onContentChange?.(finalContent)
      onSuggestionAccept?.(issue.id)
    }, 800)
  }, [editor, onContentChange, onSuggestionAccept])

  // Expose handleIssueClick via callback prop
  useEffect(() => {
    if (onIssueClick) {
      // Pass the function to parent via callback
      onIssueClick(handleIssueClick)
    }
  }, [onIssueClick, handleIssueClick])

  // Clean up replaced words when analysis is disabled
  useEffect(() => {
    if (editor && !analysisActive && replacedWords.size > 0) {
      const currentContent = editor.getHTML()
      let cleanedContent = currentContent

      replacedWords.forEach((word) => {
        cleanedContent = cleanedContent.replace(
          new RegExp(`<span class="bg-green-100 text-green-700 font-semibold animate-pulse">${word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}</span>`, 'g'),
          word
        )
      })

      if (cleanedContent !== currentContent) {
        editor.commands.setContent(cleanedContent)
        onContentChange?.(cleanedContent)
      }
      setReplacedWords(new Set())
    }
  }, [editor, analysisActive, replacedWords, onContentChange])

  if (!editor) {
    return null
  }

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
      focusChain()?.unsetFontFamily().run()
      setSelectedFont("Inter")
      return
    }

    focusChain()?.setFontFamily(family).run()
    setSelectedFont(family)
  }

  const handleFontSizeChange = (label: FontSizeLabel) => {
    if (analysisActive) return
    const value = fontSizes[label]

    // Apply fontSize using direct inline style
    const { from, to, empty } = editor.state.selection

    if (empty) {
      // No selection - set as active mark for next typed text
      editor.chain().focus().setMark('textStyle', { fontSize: value }).run()
    } else {
      // Has selection - wrap selection with fontSize style  
      editor.chain().focus().setMark('textStyle', { fontSize: value }).run()
    }

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

  const renderBlockMenuItem = (
    label: string,
    Icon: LucideIcon,
    action: () => boolean
  ) => (
    <DropdownMenuItem
      onClick={() => handleBlockSelect(label, action)}
      disabled={analysisActive}
      className={cn(
        "flex items-center gap-2 text-sm",
        selectedBlock === label && "bg-muted"
      )}
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </DropdownMenuItem>
  )

  const handleColorChange = (value: string) => {
    if (analysisActive) return
    focusChain()?.setColor(value).run()
    setFontColor(value)
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
    <Card className="border-[rgba(55,50,47,0.08)] min-h-[600px] relative shadow-sm hover:shadow-md transition-shadow duration-200">
      <CardHeader className="border-b border-[rgba(55,50,47,0.08)] bg-[#FAFAF9]">
        <div className="flex items-center justify-between mb-4">
          <CardTitle className="text-lg font-semibold text-[#37322F]">Document Editor</CardTitle>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            className="h-9 bg-white hover:bg-[#F7F5F3] min-w-[120px] justify-between border-[rgba(55,50,47,0.12)] transition-colors"
            disabled={analysisActive}
          >
            <span className="text-sm font-medium text-[#37322F]">{selectedBlock}</span>
            <ChevronDown className="h-4 w-4 text-[#605A57]" />
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
              {["Inter", "Arial", "Helvetica"].map((font) => (
                <DropdownMenuItem key={font} onClick={() => handleFontFamilyChange(font)}>
                  {font}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuLabel>Serif</DropdownMenuLabel>
              {["Times New Roman", "Garamond", "Georgia"].map((font) => (
                <DropdownMenuItem key={font} onClick={() => handleFontFamilyChange(font)}>
                  {font}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuLabel>Monospace</DropdownMenuLabel>
              {["Courier", "Courier New"].map((font) => (
                <DropdownMenuItem key={font} onClick={() => handleFontFamilyChange(font)}>
                  {font}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

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
              {Object.keys(fontSizes).map((size) => (
                <DropdownMenuItem key={size} onClick={() => handleFontSizeChange(size as keyof typeof fontSizes)}>
                  {size}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          <div className="w-px h-6 bg-[rgba(55,50,47,0.12)] self-center" />

          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 bg-white hover:bg-[#F7F5F3] border-[rgba(55,50,47,0.12)] transition-colors"
            onClick={() => editor.chain().focus().toggleBold().run()}
            disabled={!editor.can().chain().focus().toggleBold().run() || analysisActive}
          >
            <Bold className="h-4 w-4 text-[#37322F]" />
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
          <label
            className={cn(
              "relative h-9 w-9 cursor-pointer rounded-md border border-[rgba(55,50,47,0.12)] bg-white text-muted-foreground transition-colors hover:bg-[#F7F5F3] flex items-center justify-center",
              analysisActive && "pointer-events-none opacity-50"
            )}
          >
            <Palette className="h-4 w-4 text-[#37322F]" />
            <input
              type="color"
              value={fontColor}
              onChange={(event) => handleColorChange(event.target.value)}
              className="absolute inset-0 opacity-0 cursor-pointer"
              disabled={analysisActive}
            />
          </label>

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
      <CardContent className="p-0">
        <div
          className={`min-h-[600px] px-12 py-8 rounded-lg transition-all duration-200 ${analysisActive
            ? 'bg-amber-50/50'
            : 'bg-white'
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
            <EditorContent editor={editor} className="prose prose-sm max-w-none focus:outline-none" />
          )}
        </div>
      </CardContent>
    </Card>
  )
}
