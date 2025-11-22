"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useDocument } from "@/lib/document-context"
import { Button } from "@/components/ui/button"
import { Save, Download, ChevronLeft, Loader2, Check, Sparkles } from "lucide-react"
import { RichTextEditor, type AnalysisIssue } from "@/components/rich-text-editor"
import { ContextSetup } from "@/components/context-setup"
import { AnalysisIssuesOverlay } from "@/components/analysis-issues-overlay"
import { DocumentsAPI, EnhancedGoalsAPI, AnalysisAPI } from "@/lib/api-service"
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
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const initialContentRef = useRef<string>("")
  const editorHandleIssueClickRef = useRef<((issue: AnalysisIssue) => void) | null>(null)

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

  // Function to strip suggestion highlight HTML tags before saving
  const stripSuggestionHighlights = (html: string): string => {
    // Remove suggestion-applied spans but keep the text content
    // Handle both single and double quotes in class attribute
    let cleaned = html.replace(
      /<span[^>]*class="[^"]*suggestion-applied[^"]*"[^>]*>(.*?)<\/span>/gi,
      '$1'
    )
    cleaned = cleaned.replace(
      /<span[^>]*class='[^']*suggestion-applied[^']*'[^>]*>(.*?)<\/span>/gi,
      '$1'
    )
    // Also remove suggestion-applying spans
    cleaned = cleaned.replace(
      /<span[^>]*class="[^"]*suggestion-applying[^"]*"[^>]*>(.*?)<\/span>/gi,
      '$1'
    )
    cleaned = cleaned.replace(
      /<span[^>]*class='[^']*suggestion-applying[^']*'[^>]*>(.*?)<\/span>/gi,
      '$1'
    )
    return cleaned
  }

  const handleSave = async () => {
    if (!docId) return

    setIsSaving(true)
    setSaveSuccess(false)
    setError(null)

    try {
      // Strip suggestion highlight HTML tags before saving
      const cleanedContent = stripSuggestionHighlights(editorContent)
      
      await DocumentsAPI.update(docId, {
        content_full: cleanedContent,
      })

      // Update initial content ref with cleaned content
      initialContentRef.current = cleanedContent
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

  const mapErrorToIssue = (error: any, index: number): AnalysisIssue => {
    // Map backend error types to frontend issue types
    const typeMap: Record<string, AnalysisIssue["type"]> = {
      "contradiction": "logic_contradiction",
      "logic_gap": "logic_gap",
      "unsupported_claim": "weak_evidence",
      "undefined_technical_term": "clarity_issue",
      "unclear_term": "clarity_issue",
    }
    
    const issueType = typeMap[error.error_type] || "clarity_issue"
    const text = error.meta?.text || error.meta?.term || error.meta?.claim || ""
    const suggestion = error.meta?.suggestion || ""
    
    // Try to find text position in content
    let startPos = 0
    let endPos = 0
    if (text && editorContent) {
      const textLower = text.toLowerCase()
      const contentLower = editorContent.toLowerCase()
      const pos = contentLower.indexOf(textLower)
      if (pos !== -1) {
        startPos = pos
        endPos = pos + text.length
      }
    }
    
    return {
      id: error.id,
      type: issueType,
      startPos,
      endPos,
      message: error.message,
      text: text,
      suggestion: suggestion || undefined,
    }
  }

  const handleAnalyze = async () => {
    if (!docId) return
    
    if (!analysisActive) {
      // Start analysis
      setIsAnalyzing(true)
      setError(null)
      
      try {
        console.log("[Analyze] Starting analysis for document:", docId)
        
        // Trigger analysis
        const analysisResponse = await AnalysisAPI.analyze(docId)
        console.log("[Analyze] Analysis triggered:", analysisResponse)
        
        // Poll for completion (max 30 seconds)
        let attempts = 0
        const maxAttempts = 10
        let result = null
        
        while (attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 3000))
          attempts++
          
          try {
            result = await AnalysisAPI.getLatestAnalysis(docId)
            console.log("[Analyze] Attempt", attempts, "Status:", result.analysis_run.status)
            
            if (result.analysis_run.status === "completed") {
              break
            } else if (result.analysis_run.status === "failed") {
              throw new Error(result.analysis_run.error_message || "Analysis failed")
            }
          } catch (err: any) {
            // If analysis not found yet, continue polling
            if (err.message?.includes("No completed analysis")) {
              console.log("[Analyze] Analysis still running, waiting...")
              continue
            }
            throw err
          }
        }
        
        if (!result) {
          throw new Error("Analysis timeout - please try again")
        }
        
        // Map errors to issues
        const issues = result.errors.map((error, index) => mapErrorToIssue(error, index))
        console.log("[Analyze] Found", issues.length, "issues")
        
        setAnalysisIssues(issues)
        setAnalysisActive(true)
      } catch (err: any) {
        console.error("[Analyze] Error:", err)
        
        // Better error messages
        let errorMessage = "Failed to analyze document"
        if (err.message) {
          errorMessage = err.message
        } else if (err instanceof TypeError && err.message.includes("fetch")) {
          errorMessage = "Network error - please check if backend is running"
        }
        
        setError(errorMessage)
      } finally {
        setIsAnalyzing(false)
      }
    } else {
      // Disable analysis mode and clear issues
      setAnalysisIssues([])
      setAnalysisActive(false)
      setAppliedSuggestions([])
    }
  }

  const handleEditorIssueClickReady = (handleIssueClick: (issue: AnalysisIssue) => void) => {
    editorHandleIssueClickRef.current = handleIssueClick
  }

  const handleSuggestionClick = (issue: AnalysisIssue) => {
    // Call the editor's handleIssueClick function to apply the suggestion
    if (editorHandleIssueClickRef.current) {
      console.log("[Canvas] Calling editor handleIssueClick for issue:", issue.id)
      editorHandleIssueClickRef.current(issue)
    } else {
      console.warn("[Canvas] Editor handleIssueClick not available yet")
    }
    
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
            disabled={isAnalyzing}
            className={`gap-2 ${analysisActive ? 'bg-blue-600 hover:bg-blue-700' : 'bg-[#37322F] hover:bg-[#37322F]/90'}`}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                {analysisActive ? 'Analysis Active' : 'Analyze'}
              </>
            )}
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
            onIssueClick={handleEditorIssueClickReady}
          />
        </div>

        <div className="space-y-4">
          {analysisActive && analysisIssues.length > 0 ? (
            <AnalysisIssuesOverlay
              issues={analysisIssues}
              onSuggestionClick={handleSuggestionClick}
            />
          ) : (
            <ContextSetup goal={currentGoal} onApply={handleContextApply} />
          )}
        </div>
      </div>
    </div>
  )
}
