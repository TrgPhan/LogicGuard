"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useDocument } from "@/lib/document-context"
import { Button } from "@/components/ui/button"
import { Save, Download, ChevronLeft } from "lucide-react"
import { RichTextEditor } from "@/components/rich-text-editor"
import { ContextSetup } from "@/components/context-setup"

const documents: Record<string, { title: string; content: string }> = {
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

export default function CanvasPage() {
  const router = useRouter()
  const { selectedDocumentId } = useDocument()
  const [editorContent, setEditorContent] = useState("")

  if (!selectedDocumentId) {
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

  const currentDoc = documents[selectedDocumentId] || { title: "Untitled Document", content: "" }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Writing Canvas</h1>
          <p className="text-[#605A57]">
            Editing: <span className="font-medium">{currentDoc.title}</span>
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2 bg-transparent">
            <Save className="h-4 w-4" />
            Save Draft
          </Button>
          <Button className="gap-2 bg-[#37322F] hover:bg-[#37322F]/90">
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RichTextEditor onContentChange={setEditorContent} initialContent={currentDoc.content} />
        </div>

        <div className="space-y-4">
          <ContextSetup />
        </div>
      </div>
    </div>
  )
}
