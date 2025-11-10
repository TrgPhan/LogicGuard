"use client"

import { createContext, useContext, useState, type ReactNode } from "react"

interface DocumentContextType {
  selectedDocumentId: string | null
  setSelectedDocumentId: (id: string | null) => void
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined)

export function DocumentProvider({ children }: { children: ReactNode }) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null)

  return (
    <DocumentContext.Provider value={{ selectedDocumentId, setSelectedDocumentId }}>
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
