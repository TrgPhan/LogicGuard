"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useDocument } from "@/lib/document-context"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Save, Download, ChevronLeft, Sparkles } from "lucide-react"
import { RichTextEditor, AnalysisIssue } from "@/components/rich-text-editor"
import { ContextSetup } from "@/components/context-setup"
import { AnalysisIssuesOverlay } from "@/components/analysis-issues-overlay"

const mockDocuments: Record<string, { title: string; content: string }> = {
  "1": {
    title: "Research Paper Draft",
    content:
      "<p>This is a placeholder for your Research Paper Draft. The logic checking system has identified key points that align with your goal rubric and maintained your writing constraints.</p>",
  },
  "2": {
    title: "Essay on Climate Change",
    content:
      "<p>Climate change represents one of the most pressing challenges of our time. This essay explores the multifaceted impacts and proposed solutions.</p>",
  },
  "3": {
    title: "Business Proposal",
    content:
      "<p>Our business proposal outlines a comprehensive strategy for market expansion and revenue growth through strategic partnerships.</p>",
  },
  "4": {
    title: "Literature Review",
    content:
      "<p>This literature review synthesizes recent research findings in the field, identifying key themes and gaps in current knowledge.</p>",
  },
  "5": {
    title: "Case Study Analysis",
    content:
      "<p>The following case study demonstrates the practical application of theoretical frameworks in a real-world business scenario.</p>",
  },
}

const mockAnalysisIssues: AnalysisIssue[] = [
  {
    id: "1",
    type: "logic_contradiction",
    startPos: 0,
    endPos: 0,
    message: "This statement contradicts the previous argument",
    suggestion: "the system has identified consistent points",
    text: "identified key points",
  },
  {
    id: "2",
    type: "weak_evidence",
    startPos: 0,
    endPos: 0,
    message: "This claim needs stronger supporting evidence",
    suggestion: "climate change presents interconnected challenges that require evidence-based solutions",
    text: "multifaceted impacts",
  },
  {
    id: "3",
    type: "clarity_issue",
    startPos: 0,
    endPos: 0,
    message: "This phrase could be more concise and clearer",
    suggestion: "demonstrates real-world business applications",
    text: "practical application of theoretical frameworks in a real-world business scenario",
  },
  {
    id: "4",
    type: "logic_gap",
    startPos: 0,
    endPos: 0,
    message: "Missing connection between premise and conclusion",
    suggestion: "synthesizes and evaluates recent research findings",
    text: "synthesizes recent research findings",
  },
]

export default function CanvasPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { selectedDocumentId, selectedDocument } = useDocument()

  const [editorContent, setEditorContent] = useState("")
  const [currentDoc, setCurrentDoc] = useState<{ title: string; content: string } | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [analysisActive, setAnalysisActive] = useState(false)
  const [appliedSuggestions, setAppliedSuggestions] = useState<string[]>([])
  const [currentIssues, setCurrentIssues] = useState<AnalysisIssue[]>([])
  const [writingType, setWritingType] = useState<string>("essay")
  const initialContentRef = useRef<string>("")

  const docId = searchParams.get("docId") || selectedDocumentId

  useEffect(() => {
    if (docId) {
      fetchDocument(docId)
    }
  }, [docId])

  useEffect(() => {
    if (initialContentRef.current && editorContent !== initialContentRef.current) {
      setHasUnsavedChanges(true)
    } else {
      setHasUnsavedChanges(false)
    }
  }, [editorContent])

  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = ""
        return ""
      }
    }
    window.addEventListener("beforeunload", handleBeforeUnload)
    return () => window.removeEventListener("beforeunload", handleBeforeUnload)
  }, [hasUnsavedChanges])

  const fetchDocument = async (documentId: string) => {
    setIsLoading(true)
    try {
      const doc = mockDocuments[documentId] || {
        title: selectedDocument?.title || "Untitled Document",
        content: selectedDocument?.content || ""
      }
      setCurrentDoc(doc)
      setEditorContent(doc.content)
      initialContentRef.current = doc.content
      setHasUnsavedChanges(false)
    } catch (error) {
      console.error("Failed to fetch document:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSave = async () => {
    if (!docId) return

    setIsSaving(true)
    try {
      // API integration point: PUT /api/documents/{id}
      initialContentRef.current = editorContent
      setHasUnsavedChanges(false)
    } catch (error) {
      console.error("Failed to save document:", error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleExport = () => {
    // Export functionality
  }

  const handleAnalyze = () => {
    if (!analysisActive) {
      // Warn if there are unsaved changes
      if (hasUnsavedChanges) {
        const confirmed = window.confirm(
          "Bạn có thay đổi chưa được lưu. Bạn có muốn lưu trước khi phân tích không?"
        )
        if (confirmed) {
          handleSave()
        }
      }
      setCurrentIssues(mockAnalysisIssues)
    } else {
      setCurrentIssues([])
    }
    setAnalysisActive(!analysisActive)
  }

  const handleSuggestionClick = (issue: AnalysisIssue) => {
    // Don't remove here, let handleSuggestionAccept handle it after animation
    // This just triggers the animation in RichTextEditor
  }

  const handleSuggestionAccept = (issueId: string) => {
    setAppliedSuggestions([...appliedSuggestions, issueId])
    setCurrentIssues(currentIssues.filter(i => i.id !== issueId))
  }

  const handleNavigation = (path: string) => {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm(
        "Bạn có thay đổi chưa được lưu. Bạn có chắc muốn rời đi mà không lưu không?"
      )
      if (!confirmed) return
    }
    router.push(path)
  }

  if (!docId) {
    return (
      <div className="p-8 space-y-6 text-center">
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Writing Canvas</h1>
          <p className="text-[#605A57] mb-6">Please select a document to start writing</p>
          <Button onClick={() => router.push("/dashboard/documents")} className="bg-[#37322F] hover:bg-[#37322F]/90">
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="p-8 space-y-6 text-center">
        <p className="text-[#605A57]">Loading document...</p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Writing Canvas</h1>
          <p className="text-[#605A57]">
            Editing: <span className="font-medium">{currentDoc?.title}</span>
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="gap-2 bg-transparent"
            onClick={handleSave}
            disabled={isSaving || !hasUnsavedChanges}
          >
            <Save className="h-4 w-4" />
            {isSaving ? "Saving..." : "Save Draft"}
          </Button>
          <Button
            onClick={handleAnalyze}
            className={`gap-2 ${analysisActive
                ? "bg-blue-600 hover:bg-blue-700"
                : "bg-[#37322F] hover:bg-[#37322F]/90"
              }`}
          >
            <Sparkles className="h-4 w-4" />
            {analysisActive ? "Analysis Active" : "Analyze"}
          </Button>
          <Button
            className="gap-2 bg-[#37322F] hover:bg-[#37322F]/90"
            onClick={handleExport}
          >
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <RichTextEditor
            onContentChange={setEditorContent}
            initialContent={currentDoc?.content || ""}
            analysisActive={analysisActive}
            analysisIssues={currentIssues}
            onSuggestionAccept={handleSuggestionAccept}
          />
        </div>

        <div className="space-y-4 relative">
          {analysisActive && currentIssues.length > 0 && (
            <AnalysisIssuesOverlay
              issues={currentIssues}
              onSuggestionClick={handleSuggestionClick}
            />
          )}

          {(!analysisActive || currentIssues.length === 0) && (
            <>
              <Card className="border-[rgba(55,50,47,0.12)]">
                <CardHeader>
                  <CardTitle className="text-base">Writing Type</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm space-y-2">
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input
                        type="radio"
                        id="essay"
                        name="writing-type"
                        checked={writingType === "essay"}
                        onChange={() => setWritingType("essay")}
                        className="h-4 w-4"
                      />
                      <label htmlFor="essay" className="text-[#37322F] cursor-pointer">Essay</label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input
                        type="radio"
                        id="research"
                        name="writing-type"
                        checked={writingType === "research"}
                        onChange={() => setWritingType("research")}
                        className="h-4 w-4"
                      />
                      <label htmlFor="research" className="text-[#37322F] cursor-pointer">Research Paper</label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input
                        type="radio"
                        id="proposal"
                        name="writing-type"
                        checked={writingType === "proposal"}
                        onChange={() => setWritingType("proposal")}
                        className="h-4 w-4"
                      />
                      <label htmlFor="proposal" className="text-[#37322F] cursor-pointer">Business Proposal</label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input
                        type="radio"
                        id="review"
                        name="writing-type"
                        checked={writingType === "review"}
                        onChange={() => setWritingType("review")}
                        className="h-4 w-4"
                      />
                      <label htmlFor="review" className="text-[#37322F] cursor-pointer">Literature Review</label>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <ContextSetup />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
