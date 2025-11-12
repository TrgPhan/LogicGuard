"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { useRouter, useSearchParams } from "next/navigation"

export interface Document {
  id: string
  title: string
  content?: string
  date?: string
  score?: number
  words?: number
}

interface DocumentContextType {
  selectedDocumentId: string | null
  selectedDocument: Document | null
  setSelectedDocumentId: (id: string | null) => void
  setSelectedDocument: (doc: Document | null) => void
  documents: Document[]
  setDocuments: (docs: Document[]) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined)

const STORAGE_KEY = "logicguard_selected_document"

export function DocumentProvider({ children }: { children: ReactNode }) {
  const [selectedDocumentId, setSelectedDocumentIdState] = useState<string | null>(null)
  const [selectedDocument, setSelectedDocumentState] = useState<Document | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        const { id, document } = JSON.parse(stored)
        setSelectedDocumentIdState(id)
        setSelectedDocumentState(document)
      } catch (e) {
        console.error("Failed to parse stored document:", e)
      }
    }

    const docId = searchParams.get("docId")
    if (docId) {
      setSelectedDocumentIdState(docId)
    }
  }, [searchParams])

  useEffect(() => {
    if (selectedDocumentId && selectedDocument) {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          id: selectedDocumentId,
          document: selectedDocument,
        })
      )
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }, [selectedDocumentId, selectedDocument])

  const setSelectedDocumentId = (id: string | null) => {
    setSelectedDocumentIdState(id)
    if (!id) {
      setSelectedDocumentState(null)
    }
  }

  const setSelectedDocument = (doc: Document | null) => {
    setSelectedDocumentState(doc)
    if (doc) {
      setSelectedDocumentIdState(doc.id)
    }
  }

  return (
    <DocumentContext.Provider
      value={{
        selectedDocumentId,
        selectedDocument,
        setSelectedDocumentId,
        setSelectedDocument,
        documents,
        setDocuments,
        isLoading,
        setIsLoading,
      }}
    >
      {children}
    </DocumentContext.Provider>
  )
}

export function useDocument() {
  const context = useContext(DocumentContext)
  if (context === undefined) {
    throw new Error("useDocument must be used within DocumentProvider")
  }
  return context
}
