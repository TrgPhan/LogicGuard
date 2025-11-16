"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useDocument } from "@/lib/document-context"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Target, TrendingUp, CheckCircle2, AlertCircle, ChevronLeft } from "lucide-react"

interface GoalMetric {
  name: string
  value: number
  target: number
  status: "excellent" | "good" | "warning" | "poor"
}

interface GoalsData {
  metrics: GoalMetric[]
  overallProgress: number
}

const mockGoalsData: Record<string, GoalsData> = {
  "1": {
    metrics: [
      { name: "Rubric Coverage", value: 85, target: 90, status: "good" },
      { name: "Argument Coherence", value: 72, target: 80, status: "warning" },
      { name: "Evidence Quality", value: 90, target: 85, status: "excellent" },
      { name: "Logical Flow", value: 68, target: 75, status: "warning" },
    ],
    overallProgress: 78,
  },
  "2": {
    metrics: [
      { name: "Rubric Coverage", value: 92, target: 90, status: "excellent" },
      { name: "Argument Coherence", value: 88, target: 80, status: "excellent" },
      { name: "Evidence Quality", value: 85, target: 85, status: "good" },
      { name: "Logical Flow", value: 80, target: 75, status: "good" },
    ],
    overallProgress: 86,
  },
}

export default function GoalsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { selectedDocumentId } = useDocument()

  const [goalsData, setGoalsData] = useState<GoalsData | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const docId = searchParams.get("docId") || selectedDocumentId

  useEffect(() => {
    if (docId) {
      fetchGoals(docId)
    }
  }, [docId])

  const fetchGoals = async (documentId: string) => {
    setIsLoading(true)
    try {
      setGoalsData(mockGoalsData[documentId] || mockGoalsData["1"])
    } catch (error) {
      // Silent fail
    } finally {
      setIsLoading(false)
    }
  }

  if (!docId) {
    return (
      <div className="p-8 space-y-6 text-center">
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Goal Alignment Dashboard</h1>
          <p className="text-[#605A57] mb-6">Please select a document to view goal alignment</p>
          <Button onClick={() => router.push("/dashboard/documents")} className="bg-[#37322F] hover:bg-[#37322F]/90">
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
        </div>
      </div>
    )
  }

  if (isLoading || !goalsData) {
    return (
      <div className="p-8 space-y-6 text-center">
        <p className="text-[#605A57]">Loading goals...</p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Goal Alignment Dashboard</h1>
        <p className="text-[#605A57]">Track your writing progress and goal achievement</p>
      </div>

      {/* Overall Progress */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">Overall Progress</CardTitle>
              <CardDescription>Your writing is {goalsData.overallProgress}% aligned with your goals</CardDescription>
            </div>
            <Target className="h-8 w-8 text-[#37322F]" />
          </div>
        </CardHeader>
        <CardContent>
          <Progress value={goalsData.overallProgress} className="h-3" />
        </CardContent>
      </Card>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {goalsData.metrics.map((metric, index) => {
          const getStatusColor = (status: string) => {
            switch (status) {
              case "excellent":
                return "text-green-600"
              case "good":
                return "text-blue-600"
              case "warning":
                return "text-yellow-600"
              default:
                return "text-red-600"
            }
          }

          const getStatusIcon = (status: string) => {
            switch (status) {
              case "excellent":
              case "good":
                return <CheckCircle2 className="h-5 w-5 text-green-600" />
              default:
                return <AlertCircle className="h-5 w-5 text-yellow-600" />
            }
          }

          return (
            <Card key={index} className="border-[rgba(55,50,47,0.12)]">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{metric.name}</CardTitle>
                    <CardDescription>Target: {metric.target}%</CardDescription>
                  </div>
                  {getStatusIcon(metric.status)}
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-end gap-2">
                  <span className={`text-3xl font-bold ${getStatusColor(metric.status)}`}>{metric.value}%</span>
                  <span className="text-sm text-[#605A57] mb-1">
                    {metric.value >= metric.target ? "Above target" : `${metric.target - metric.value}% to go`}
                  </span>
                </div>
                <Progress value={metric.value} className="h-2" />
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recommendations */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Recommendations
          </CardTitle>
          <CardDescription>Actions to improve your goal alignment</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              "Strengthen your argument coherence by adding transitional phrases between paragraphs",
              "Improve logical flow by reorganizing sections 3 and 4",
              "Add more specific examples to increase evidence quality",
            ].map((recommendation, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-[#F7F5F3] rounded-lg">
                <div className="mt-0.5">
                  <div className="h-2 w-2 rounded-full bg-[#37322F]" />
                </div>
                <p className="text-sm text-[#37322F]">{recommendation}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
