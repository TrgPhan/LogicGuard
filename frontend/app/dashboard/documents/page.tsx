"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useDocument, type Document } from "@/lib/document-context"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Plus, MoreVertical } from "lucide-react"
import { DocxUploadButton } from "@/components/docx-upload-button"

export default function DocumentsPage() {
  const router = useRouter()
  const { setSelectedDocument, documents, setDocuments } = useDocument()
  const [isLoading, setIsLoading] = useState(false)

  const mockDocuments: Document[] = [
    { id: "1", title: "Research Paper Draft", date: "2 hours ago", score: 92, words: 2450 },
    { id: "2", title: "Essay on Climate Change", date: "Yesterday", score: 85, words: 1820 },
    { id: "3", title: "Business Proposal", date: "3 days ago", score: 78, words: 3200 },
    { id: "4", title: "Literature Review", date: "1 week ago", score: 88, words: 4100 },
    { id: "5", title: "Case Study Analysis", date: "2 weeks ago", score: 91, words: 2900 },
  ]

  useEffect(() => {
    setDocuments(mockDocuments)
  }, [])

  const handleDocumentClick = (doc: Document) => {
    setSelectedDocument(doc)

    const params = new URLSearchParams()
    params.set("docId", doc.id)
    router.push(`/dashboard/canvas?${params.toString()}`)
  }

  const handleContentImport = (content: string, fileName: string) => {
    const newDoc: Document = {
      id: Date.now().toString(),
      title: fileName.replace(".docx", ""),
      content: content,
      date: "Just now",
      score: 0,
      words: content.split(" ").length,
    }

    setSelectedDocument(newDoc)
    setDocuments([newDoc, ...documents])

    const params = new URLSearchParams()
    params.set("docId", newDoc.id)
    router.push(`/dashboard/canvas?${params.toString()}`)
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
          <Button className="gap-2 bg-[#37322F] hover:bg-[#37322F]/90">
            <Plus className="h-4 w-4" />
            New Document
          </Button>
        </div>
      </div>

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
    </div>
  )
}
