"use client"

import { useRouter } from "next/navigation"
import { useDocument } from "@/lib/document-context"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertCircle, AlertTriangle, Info, ChevronLeft } from "lucide-react"

const documentFeedback: Record<
  string,
  Array<{ severity: string; type: string; message: string; location: string; suggestion: string }>
> = {
  "1": [
    {
      severity: "high",
      type: "Logical Contradiction",
      message: "The argument in paragraph 3 contradicts the claim made in paragraph 1",
      location: "Paragraph 3, Line 2",
      suggestion: "Consider revising to maintain consistency with your initial claim",
    },
    {
      severity: "medium",
      type: "Weak Evidence",
      message: "The evidence provided doesn't strongly support the conclusion",
      location: "Paragraph 5, Line 4",
      suggestion: "Add more specific data or examples to strengthen your argument",
    },
    {
      severity: "low",
      type: "Clarity Issue",
      message: "This sentence could be more concise and clear",
      location: "Paragraph 2, Line 1",
      suggestion: "Simplify the sentence structure for better readability",
    },
  ],
  "2": [
    {
      severity: "medium",
      type: "Missing Evidence",
      message: "Climate impact claims need stronger evidence",
      location: "Paragraph 4",
      suggestion: "Add recent statistics or scientific studies",
    },
  ],
}

export default function FeedbackPage() {
  const router = useRouter()
  const { selectedDocumentId } = useDocument()

  if (!selectedDocumentId) {
    return (
      <div className="p-8 space-y-6 text-center">
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Contextual Feedback</h1>
          <p className="text-[#605A57] mb-6">Please select a document to view feedback</p>
          <Button onClick={() => router.push("/dashboard/documents")} className="bg-[#37322F] hover:bg-[#37322F]/90">
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
        </div>
      </div>
    )
  }

  const feedbackItems = documentFeedback[selectedDocumentId] || documentFeedback["1"]

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "high":
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      default:
        return <Info className="h-5 w-5 text-blue-500" />
    }
  }

  const getSeverityBadge = (severity: string) => {
    const variants: Record<string, string> = {
      high: "bg-red-100 text-red-700 border-red-200",
      medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
      low: "bg-blue-100 text-blue-700 border-blue-200",
    }
    return variants[severity] || variants.low
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Contextual Feedback</h1>
        <p className="text-[#605A57]">Review logic issues and suggestions for your writing</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-[rgba(55,50,47,0.12)]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-[#605A57]">High Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {feedbackItems.filter((f) => f.severity === "high").length}
            </div>
          </CardContent>
        </Card>
        <Card className="border-[rgba(55,50,47,0.12)]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-[#605A57]">Medium Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-600">
              {feedbackItems.filter((f) => f.severity === "medium").length}
            </div>
          </CardContent>
        </Card>
        <Card className="border-[rgba(55,50,47,0.12)]">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-[#605A57]">Low Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {feedbackItems.filter((f) => f.severity === "low").length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feedback List */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-[#37322F]">All Feedback</h2>
        {feedbackItems.map((item, index) => (
          <Card key={index} className="border-[rgba(55,50,47,0.12)]">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  {getSeverityIcon(item.severity)}
                  <div>
                    <CardTitle className="text-lg">{item.type}</CardTitle>
                    <CardDescription className="mt-1">{item.location}</CardDescription>
                  </div>
                </div>
                <Badge className={getSeverityBadge(item.severity)}>{item.severity.toUpperCase()}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <p className="text-sm font-medium text-[#37322F] mb-1">Issue:</p>
                <p className="text-sm text-[#605A57]">{item.message}</p>
              </div>
              <div className="p-3 bg-[#F7F5F3] rounded-lg">
                <p className="text-sm font-medium text-[#37322F] mb-1">Suggestion:</p>
                <p className="text-sm text-[#605A57]">{item.suggestion}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
