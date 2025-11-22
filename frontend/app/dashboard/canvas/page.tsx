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
import { getApiBaseUrlWithoutSuffix } from "@/lib/api-config"

interface ContextDataPayload {
  writingType: string
  goalRubrics: string[]
  keyConstraints: string[]
  goal: GoalDetailResponse
}

// Item trả về từ backend unified /logic-checks/undefined-terms
interface LogicIssueItem {
  id?: string
  type?: AnalysisIssue["type"] | string
  text?: string
  term?: string
  reason?: string
  suggestion?: string
  start_pos?: number
  end_pos?: number
}

interface LogicAnalysisAPIResponse {
  success?: boolean
  content?: string
  context?: any
  total_terms_found?: number
  total_undefined?: number
  metadata?: Record<string, any>
  items?: LogicIssueItem[]
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

  const docId = searchParams?.get("docId") ?? selectedDocumentId ?? null

  useEffect(() => {
    if (docId) {
      void fetchDocument(docId)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
        "Bạn có thay đổi chưa được lưu. Bạn có chắc muốn rời đi mà không lưu không?",
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
        content,
        goalId: doc.goal_id,
      })
      setEditorContent(content)
      initialContentRef.current = content
      setHasUnsavedChanges(false)

      if (doc.goal_id) {
        await loadGoal(doc.goal_id)
      }
    } catch (err: unknown) {
      const e = err as Error
      setError(e.message || "Failed to load document")
      if (selectedDocument) {
        const content = selectedDocument.content || ""
        setCurrentDoc({
          title: selectedDocument.title,
          content,
          goalId: undefined,
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
    } catch (err: unknown) {
      const e = err as Error
      setError(e.message || "Failed to load goal data")
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
    } catch (err: unknown) {
      const e = err as Error
      setError(e.message || "Failed to save document")
    } finally {
      setIsSaving(false)
    }
  }

  const handleExport = () => {
    if (!currentDoc) return

    const blob = new Blob([editorContent], { type: "text/html" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
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

        setCurrentDoc(prev => (prev ? { ...prev, goalId: contextData.goal.id } : prev))
      }

      setCurrentGoal(contextData.goal)
    } catch (err: unknown) {
      const e = err as Error
      setError(e.message || "Failed to link goal to document")
    }
  }

  const handleAnalyze = async () => {
    // Nếu đang bật thì tắt phân tích, clear issues
    if (analysisActive) {
      setAnalysisIssues([])
      setAnalysisActive(false)
      setAppliedSuggestions([])
      return
    }

    // Bật chế độ phân tích
    setAnalysisActive(true)
    setError(null)

    try {
      // Lấy content hiện tại trong editor
      const content = editorContent || currentDoc?.content || ""

      if (!content.trim()) {
        setError("Không có nội dung để phân tích")
        setAnalysisIssues([])
        setAnalysisActive(false)
        return
      }

      // Lấy token giống cách login đang dùng
      let token: string | null = null

      if (typeof window !== "undefined") {
        token =
          localStorage.getItem("access_token") ||
          localStorage.getItem("accessToken") ||
          localStorage.getItem("token") ||
          sessionStorage.getItem("access_token") ||
          sessionStorage.getItem("accessToken") ||
          sessionStorage.getItem("token")

        console.log("[Canvas] token found?", !!token)
      }

      if (!token) {
        setError("Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn.")
        setAnalysisIssues([])
        setAnalysisActive(false)
        return
      }

      // Context đơn giản; sau này có thể dùng currentGoal để enrich thêm
      const mainGoalTitle = currentGoal
        ? "Analyze document for current goal"
        : "Analyze document for logical issues"

      const contextPayload = {
        writing_type: "Document",
        main_goal: mainGoalTitle,
        criteria: [],
        constraints: [],
      }

      const baseUrl = getApiBaseUrlWithoutSuffix()

      const res = await fetch(`${baseUrl}/api/logic-checks/undefined-terms`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
        body: JSON.stringify({
          context: contextPayload,
          content,
        }),
      })

      if (res.status === 401 || res.status === 403) {
        const text = await res.text()
        console.error("[Canvas] Unauthorized/Forbidden:", res.status, text)
        setError("Bạn chưa đăng nhập hoặc không có quyền sử dụng tính năng phân tích.")
        setAnalysisIssues([])
        setAnalysisActive(false)
        return
      }

      if (!res.ok) {
        const text = await res.text()
        console.error("[Canvas] Analysis API error:", res.status, text)
        setError("Phân tích thất bại từ server")
        setAnalysisIssues([])
        setAnalysisActive(false)
        return
      }

      const data: LogicAnalysisAPIResponse = await res.json()
      const items: LogicIssueItem[] = data.items ?? []

      const mapped: AnalysisIssue[] = items.map((item, index) => ({
        id: item.id ?? String(index + 1),
        type: (item.type as AnalysisIssue["type"]) || "clarity_issue",
        startPos: item.start_pos ?? 0,
        endPos: item.end_pos ?? 0,
        text: item.text || item.term || "",
        message: item.reason || "",
        suggestion: item.suggestion || "",
      }))

      console.log("[Canvas] mapped issues:", mapped.length)
      setAnalysisIssues(mapped)
    } catch (err: unknown) {
      console.error("[Canvas] Analysis failed:", err)
      if (err instanceof Error) {
        setError(err.message || "Phân tích thất bại")
      } else {
        setError("Phân tích thất bại")
      }
      setAnalysisIssues([])
      setAnalysisActive(false)
    }
  }

  const handleSuggestionClick = (issue: AnalysisIssue) => {
    setAnalysisIssues(analysisIssues.filter(i => i.id !== issue.id))
    setAppliedSuggestions([...appliedSuggestions, issue.id])
  }

  const handleSuggestionAccept = (issueId: string) => {
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
            className={`gap-2 ${
              analysisActive ? "bg-blue-600 hover:bg-blue-700" : "bg-[#37322F] hover:bg-[#37322F]/90"
            }`}
          >
            <Sparkles className="h-4 w-4" />
            {analysisActive ? "Analysis Active" : "Analyze"}
          </Button>
          <Button className="gap-2 bg-[#37322F] hover:bg-[#37322F]/90" onClick={handleExport}>
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
            <AnalysisIssuesOverlay issues={analysisIssues} onSuggestionClick={handleSuggestionClick} />
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
                      <label htmlFor="essay" className="text-[#37322F] cursor-pointer">
                        Essay
                      </label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input type="radio" id="research" name="writing-type" className="h-4 w-4" />
                      <label htmlFor="research" className="text-[#37322F] cursor-pointer">
                        Research Paper
                      </label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input type="radio" id="proposal" name="writing-type" className="h-4 w-4" />
                      <label htmlFor="proposal" className="text-[#37322F] cursor-pointer">
                        Business Proposal
                      </label>
                    </div>
                    <div className="flex items-center gap-2 p-2 rounded hover:bg-[#F7F5F3] cursor-pointer">
                      <input type="radio" id="review" name="writing-type" className="h-4 w-4" />
                      <label htmlFor="review" className="text-[#37322F] cursor-pointer">
                        Literature Review
                      </label>
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
