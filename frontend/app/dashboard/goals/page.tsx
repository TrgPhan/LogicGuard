"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Target, TrendingUp, CheckCircle2, AlertCircle } from "lucide-react"

export default function GoalsPage() {
  const metrics = [
    { name: "Rubric Coverage", value: 85, target: 90, status: "good" },
    { name: "Argument Coherence", value: 72, target: 80, status: "warning" },
    { name: "Evidence Quality", value: 90, target: 85, status: "excellent" },
    { name: "Logical Flow", value: 68, target: 75, status: "warning" },
  ]

  return (
    <DashboardLayout>
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
                <CardDescription>Your writing is 78% aligned with your goals</CardDescription>
              </div>
              <Target className="h-8 w-8 text-[#37322F]" />
            </div>
          </CardHeader>
          <CardContent>
            <Progress value={78} className="h-3" />
          </CardContent>
        </Card>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {metrics.map((metric, index) => {
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
    </DashboardLayout>
  )
}
