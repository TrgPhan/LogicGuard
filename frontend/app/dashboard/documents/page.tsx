"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useDocument, type Document } from "@/lib/document-context"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Plus, MoreVertical, Loader2 } from "lucide-react"
import { DocxUploadButton } from "@/components/docx-upload-button"
import { DocumentsAPI } from "@/lib/api-service"
import { formatDistanceToNow } from "date-fns"

export default function DocumentsPage() {
  const router = useRouter()
  const { setSelectedDocument, documents, setDocuments } = useDocument()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const docs = await DocumentsAPI.getAll()
      const formattedDocs = docs.map(doc => ({
        id: doc.id,
        title: doc.title,
        date: formatDistanceToNow(new Date(doc.updated_at), { addSuffix: true }),
        words: doc.word_count,
      }))
      setDocuments(formattedDocs)
    } catch (err: any) {
      setError(err.message || "Failed to load documents")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDocumentClick = (doc: Document) => {
    setSelectedDocument(doc)

    const params = new URLSearchParams()
    params.set("docId", doc.id)
    router.push(`/dashboard/canvas?${params.toString()}`)
  }

  const handleContentImport = async (content: string, fileName: string) => {
    try {
      const newDoc = await DocumentsAPI.create({
        title: fileName.replace(".docx", ""),
        content_full: content,
      })

      const formattedDoc: Document = {
        id: newDoc.id,
        title: newDoc.title,
        content: newDoc.content_full,
        date: "Just now",
        words: newDoc.word_count,
      }

      setSelectedDocument(formattedDoc)
      setDocuments([formattedDoc, ...documents])

      const params = new URLSearchParams()
      params.set("docId", newDoc.id)
      router.push(`/dashboard/canvas?${params.toString()}`)
    } catch (err: any) {
      setError(err.message || "Failed to import document")
    }
  }

  const handleCreateNew = async () => {
    try {
      const newDoc = await DocumentsAPI.create({
        title: "Untitled Document",
        content_full: "",
      })

      const formattedDoc: Document = {
        id: newDoc.id,
        title: newDoc.title,
        date: "Just now",
        words: 0,
      }

      setSelectedDocument(formattedDoc)
      setDocuments([formattedDoc, ...documents])

      const params = new URLSearchParams()
      params.set("docId", newDoc.id)
      router.push(`/dashboard/canvas?${params.toString()}`)
    } catch (err: any) {
      setError(err.message || "Failed to create document")
    }
  }

  return (
    <div className="p-8 space-y-6" data-section="documents">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Documents</h1>
          <p className="text-[#605A57]">Manage all your writing projects</p>
        </div>
        <div className="flex gap-2">
          <DocxUploadButton onContentParsed={handleContentImport} />
          <Button onClick={handleCreateNew} className="gap-2 bg-[#37322F] hover:bg-[#37322F]/90">
            <Plus className="h-4 w-4" />
            New Document
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#37322F]" />
        </div>
      )}

      {!isLoading && documents.length === 0 && (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-[#605A57] mx-auto mb-4" />
          <p className="text-[#605A57]">No documents yet. Create your first one!</p>
        </div>
      )}

      {!isLoading && documents.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <Card
              key={doc.id}
              className="border-[rgba(55,50,47,0.12)] hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleDocumentClick(doc)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-2 bg-[#F7F5F3] rounded-lg">
                    <FileText className="h-6 w-6 text-[#37322F]" />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={(e) => {
                      e.stopPropagation()
                    }}
                  >
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
                <h3 className="font-semibold text-[#37322F] mb-2 line-clamp-2">{doc.title}</h3>
                <p className="text-sm text-[#605A57] mb-4">{doc.date}</p>
                <div className="flex items-center justify-between pt-4 border-t border-[rgba(55,50,47,0.12)]">
                  {/* Logic Score - Hidden until Analysis API is implemented
                <div>
                  <p className="text-xs text-[#605A57]">Logic Score</p>
                  <p className="text-lg font-semibold text-[#37322F]">{doc.score}%</p>
                </div>
                */}
                  <div>
                    <p className="text-xs text-[#605A57]">Words</p>
                    <p className="text-lg font-semibold text-[#37322F]">{doc.words?.toLocaleString() || 0}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-[#605A57]">Last Updated</p>
                    <p className="text-sm text-[#605A57]">{doc.date}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
