"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, File } from "lucide-react"

interface DocxUploadProps {
  onContentParsed?: (content: string) => void
}

export function DocxUpload({ onContentParsed }: DocxUploadProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [fileName, setFileName] = useState<string>("")

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith(".docx")) {
      alert("Please upload a .docx file")
      return
    }

    setIsLoading(true)
    setFileName(file.name)

    try {
      // Dynamically import mammoth
      const mammoth = await import("mammoth")

      const arrayBuffer = await file.arrayBuffer()
      const result = await mammoth.convertToHtml({ arrayBuffer })

      // Parse and format the HTML content
      const htmlContent = result.value
      onContentParsed?.(htmlContent)
    } catch (error) {
      console.error("Error parsing document:", error)
      alert("Error parsing document. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="border-[rgba(55,50,47,0.12)]">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Import Document
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative">
          <input
            type="file"
            accept=".docx"
            onChange={handleFileUpload}
            disabled={isLoading}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
          />
          <Button
            disabled={isLoading}
            variant="outline"
            className="w-full gap-2 border-[rgba(55,50,47,0.12)] bg-transparent"
          >
            <File className="h-4 w-4" />
            {isLoading ? "Uploading..." : "Upload .docx"}
          </Button>
        </div>
        {fileName && (
          <p className="text-sm text-[#605A57] text-center">
            Loaded: <span className="font-medium">{fileName}</span>
          </p>
        )}
        <p className="text-xs text-[#605A57] text-center">
          Upload a Word document (.docx) to import content into the editor
        </p>
      </CardContent>
    </Card>
  )
}
