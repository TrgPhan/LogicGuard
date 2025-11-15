"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useDocument } from "@/lib/document-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Save, Download, ChevronLeft, Loader2, Check, Sparkles } from "lucide-react"
import { RichTextEditor, type AnalysisIssue } from "@/components/rich-text-editor"
import { ContextSetup } from "@/components/context-setup"
import { AnalysisIssuesOverlay } from "@/components/analysis-issues-overlay"
import { DocumentsAPI, EnhancedGoalsAPI } from "@/lib/api-service"
import type { GoalDetailResponse } from "@/lib/api-service"

interface ContextDataPayload {
  writingType: string
  goalRubrics: string[]
  keyConstraints: string[]
  goal: GoalDetailResponse
}

export default function CanvasPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { selectedDocumentId, selectedDocument } = useDocument()

  const [editorContent, setEditorContent] = useState("")
  const [currentDoc, setCurrentDoc] = useState<{ title: string; content: string; goalId?: string | null } | null>(null)
  const [currentGoal, setCurrentGoal] = useState<GoalDetailResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [analysisActive, setAnalysisActive] = useState(false)
  const [analysisIssues, setAnalysisIssues] = useState<AnalysisIssue[]>([])
  const [appliedSuggestions, setAppliedSuggestions] = useState<string[]>([])
  const initialContentRef = useRef<string>("")

  const docId = searchParams.get("docId") || selectedDocumentId

  // Mock analysis issues - Replace with actual API call
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

  useEffect(() => {
    if (docId) {
      fetchDocument(docId)
    }
  }, [docId])

  // Track unsaved changes
  useEffect(() => {
    if (initialContentRef.current && editorContent !== initialContentRef.current) {
      setHasUnsavedChanges(true)
    } else {
      setHasUnsavedChanges(false)
    }
  }, [editorContent])

  // Warn before leaving page with unsaved changes
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

  // Intercept router navigation
  const handleNavigation = (path: string) => {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm(
        "Bạn có thay đổi chưa được lưu. Bạn có chắc muốn rời đi mà không lưu không?"
      )
      if (!confirmed) return
    }
    router.push(path)
  }

  const fetchDocument = async (documentId: string) => {
    setIsLoading(true)
    setError(null)
    setCurrentGoal(null)
    try {
      const doc = await DocumentsAPI.getById(documentId)
      const content = doc.content_full || ""
      setCurrentDoc({
        title: doc.title,
        content: content,
        goalId: doc.goal_id
      })
      setEditorContent(content)
      initialContentRef.current = content
      setHasUnsavedChanges(false)

      if (doc.goal_id) {
        await loadGoal(doc.goal_id)
      }
    } catch (err: any) {
      setError(err.message || "Failed to load document")
      if (selectedDocument) {
        const content = selectedDocument.content || ""
        setCurrentDoc({
          title: selectedDocument.title,
          content: content,
          goalId: undefined
        })
        setEditorContent(content)
        initialContentRef.current = content
      }
    } finally {
      setIsLoading(false)
    }
  }

  const loadGoal = async (goalId: string) => {
    try {
      const goalData = await EnhancedGoalsAPI.getById(goalId)
      setCurrentGoal(goalData)
    } catch (err: any) {
      setError(err.message || "Failed to load goal data")
    }
  }

  const handleSave = async () => {
    if (!docId) return

    setIsSaving(true)
    setSaveSuccess(false)
    setError(null)

    try {
      await DocumentsAPI.update(docId, {
        content_full: editorContent,
      })

      initialContentRef.current = editorContent
      setHasUnsavedChanges(false)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 2000)
    } catch (err: any) {
      setError(err.message || "Failed to save document")
    } finally {
      setIsSaving(false)
    }
  }

  const handleExport = () => {
    if (!currentDoc) return

    const blob = new Blob([editorContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentDoc.title}.html`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const handleContextApply = async (contextData: ContextDataPayload) => {
    if (!docId || !contextData.goal) return

    try {
      if (!currentDoc?.goalId || currentDoc.goalId !== contextData.goal.id) {
        await DocumentsAPI.update(docId, {
          goal_id: contextData.goal.id,
        })

        setCurrentDoc((prev) => (prev ? { ...prev, goalId: contextData.goal.id } : prev))
      }

      setCurrentGoal(contextData.goal)
    } catch (err: any) {
      setError(err.message || "Failed to link goal to document")
    }
  }

  const handleAnalyze = () => {
    if (!analysisActive) {
      // Enable analysis mode and show mock issues
      setAnalysisIssues(mockAnalysisIssues)
      setAnalysisActive(true)
    } else {
      // Disable analysis mode and clear issues
      setAnalysisIssues([])
      setAnalysisActive(false)
      setAppliedSuggestions([])
    }
  }

  const handleSuggestionClick = (issue: AnalysisIssue) => {
    // Remove the issue from the list when clicked
    setAnalysisIssues(analysisIssues.filter(i => i.id !== issue.id))
    setAppliedSuggestions([...appliedSuggestions, issue.id])
  }

  const handleSuggestionAccept = (issueId: string) => {
    // Called after suggestion is applied in editor
    console.log("[Canvas] Suggestion accepted:", issueId)
  }

  if (!docId) {
    return (
      <div className="p-8 space-y-6 text-center">
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Writing Canvas</h1>
          <p className="text-[#605A57] mb-6">Please select a document to start writing</p>
          <Button
            onClick={() => handleNavigation("/dashboard/documents")}
            className="bg-[#37322F] hover:bg-[#37322F]/90"
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="p-8 space-y-6 flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-[#37322F]" />
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

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
            {isSaving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : saveSuccess ? (
              <Check className="h-4 w-4 text-green-600" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {isSaving ? "Saving..." : saveSuccess ? "Saved!" : "Save Draft"}
          </Button>
          <Button
            onClick={handleAnalyze}
            className={`gap-2 ${analysisActive ? 'bg-blue-600 hover:bg-blue-700' : 'bg-[#37322F] hover:bg-[#37322F]/90'}`}
          >
            <Sparkles className="h-4 w-4" />
            {analysisActive ? 'Analysis Active' : 'Analyze'}
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
        <div className="lg:col-span-2">
          <RichTextEditor
            onContentChange={setEditorContent}
            initialContent={currentDoc?.content || ""}
            analysisActive={analysisActive}
            analysisIssues={analysisIssues}
            onSuggestionAccept={handleSuggestionAccept}
          />
        </div>

        <div className="space-y-4">
          {analysisActive && analysisIssues.length > 0 ? (
            <AnalysisIssuesOverlay
              issues={analysisIssues}
              onSuggestionClick={handleSuggestionClick}
            />
          ) : (
            <>
              <Card className="border-[rgba(55,50,47,0.12)]">
                <CardHeader>
                  <CardTitle className="text-base">Writing Type</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm space-y-2">
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input type="radio" id="essay" name="writing-type" defaultChecked className="h-4 w-4" />
                      <label htmlFor="essay" className="text-[#37322F] cursor-pointer">Essay</label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input type="radio" id="research" name="writing-type" className="h-4 w-4" />
                      <label htmlFor="research" className="text-[#37322F] cursor-pointer">Research Paper</label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input type="radio" id="proposal" name="writing-type" className="h-4 w-4" />
                      <label htmlFor="proposal" className="text-[#37322F] cursor-pointer">Business Proposal</label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input type="radio" id="review" name="writing-type" className="h-4 w-4" />
                      <label htmlFor="review" className="text-[#37322F] cursor-pointer">Literature Review</label>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <ContextSetup goal={currentGoal} onApply={handleContextApply} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
