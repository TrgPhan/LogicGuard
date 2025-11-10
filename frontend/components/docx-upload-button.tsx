"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Upload } from "lucide-react"

interface DocxUploadButtonProps {
  onContentParsed?: (content: string, fileName: string) => void
}

export function DocxUploadButton({ onContentParsed }: DocxUploadButtonProps) {
  const [isLoading, setIsLoading] = useState(false)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith(".docx")) {
      alert("Please upload a .docx file")
      return
    }

    setIsLoading(true)

    try {
      const mammoth = await import("mammoth")
      const arrayBuffer = await file.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })
      onContentParsed?.(result.value, file.name)
    } catch (error) {
      console.error("Error parsing document:", error)
      alert("Error parsing document. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative inline-block">
      <input
        type="file"
        accept=".docx"
        onChange={handleFileUpload}
        disabled={isLoading}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
      />
      <Button disabled={isLoading} variant="outline" className="gap-2 bg-transparent">
        <Upload className="h-4 w-4" />
        {isLoading ? "Importing..." : "Import .docx"}
      </Button>
    </div>
  )
}
