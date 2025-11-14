"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useDocument } from "@/lib/document-context"
import { Button } from "@/components/ui/button"
import { Save, Download, ChevronLeft, Loader2, Check } from "lucide-react"
import { RichTextEditor } from "@/components/rich-text-editor"
import { ContextSetup } from "@/components/context-setup"
import { DocumentsAPI } from "@/lib/api-service"

export default function CanvasPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { selectedDocumentId, selectedDocument } = useDocument()

  const [editorContent, setEditorContent] = useState("")
  const [currentDoc, setCurrentDoc] = useState<{ title: string; content: string; goalId?: string | null } | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const initialContentRef = useRef<string>("")

  const docId = searchParams.get("docId") || selectedDocumentId

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

  const handleContextApply = async (contextData: any) => {
    if (!docId || !contextData.goal) return

    try {
      await DocumentsAPI.update(docId, {
        goal_id: contextData.goal.id,
      })
      
      setCurrentDoc(prev => prev ? { ...prev, goalId: contextData.goal.id } : null)
    } catch (err: any) {
      setError(err.message || "Failed to link goal to document")
    }
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
          />
        </div>

        <div className="space-y-4">
          <ContextSetup onApply={handleContextApply} />
        </div>
      </div>
    </div>
  )
}
