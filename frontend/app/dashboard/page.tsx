"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PenTool, MessageSquare, Target, FileText, TrendingUp, CheckCircle2 } from "lucide-react"

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="p-8 space-y-8">
        {/* Welcome Section */}
        <div>
          <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Welcome back!</h1>
          <p className="text-[#605A57]">Here's an overview of your writing progress and tools.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-[rgba(55,50,47,0.12)]">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-[#605A57]">Total Documents</CardTitle>
              <FileText className="h-4 w-4 text-[#605A57]" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-[#37322F]">12</div>
              <p className="text-xs text-[#605A57] mt-1">+2 from last week</p>
            </CardContent>
          </Card>

          <Card className="border-[rgba(55,50,47,0.12)]">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-[#605A57]">Logic Score</CardTitle>
              <TrendingUp className="h-4 w-4 text-[#605A57]" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-[#37322F]">87%</div>
              <p className="text-xs text-[#605A57] mt-1">+5% improvement</p>
            </CardContent>
          </Card>

          <Card className="border-[rgba(55,50,47,0.12)]">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-[#605A57]">Issues Resolved</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-[#605A57]" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-[#37322F]">34</div>
              <p className="text-xs text-[#605A57] mt-1">This month</p>
            </CardContent>
          </Card>

          <Card className="border-[rgba(55,50,47,0.12)]">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-[#605A57]">Goal Progress</CardTitle>
              <Target className="h-4 w-4 text-[#605A57]" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-[#37322F]">68%</div>
              <p className="text-xs text-[#605A57] mt-1">On track</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-xl font-semibold text-[#37322F] mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card className="border-[rgba(55,50,47,0.12)] hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#F7F5F3] rounded-lg">
                    <PenTool className="h-6 w-6 text-[#37322F]" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Start Writing</CardTitle>
                    <CardDescription>Open the writing canvas</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            <Card className="border-[rgba(55,50,47,0.12)] hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#F7F5F3] rounded-lg">
                    <MessageSquare className="h-6 w-6 text-[#37322F]" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Review Feedback</CardTitle>
                    <CardDescription>Check logic suggestions</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            <Card className="border-[rgba(55,50,47,0.12)] hover:shadow-md transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-[#F7F5F3] rounded-lg">
                    <Target className="h-6 w-6 text-[#37322F]" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Set Goals</CardTitle>
                    <CardDescription>Define writing objectives</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </div>
        </div>

        {/* Recent Documents */}
        <div>
          <h2 className="text-xl font-semibold text-[#37322F] mb-4">Recent Documents</h2>
          <Card className="border-[rgba(55,50,47,0.12)]">
            <CardContent className="p-0">
              <div className="divide-y divide-[rgba(55,50,47,0.12)]">
                {[
                  { title: "Research Paper Draft", date: "2 hours ago", score: 92 },
                  { title: "Essay on Climate Change", date: "Yesterday", score: 85 },
                  { title: "Business Proposal", date: "3 days ago", score: 78 },
                ].map((doc, index) => (
                  <div key={index} className="p-4 hover:bg-[#F7F5F3] cursor-pointer transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-[#605A57]" />
                        <div>
                          <p className="font-medium text-[#37322F]">{doc.title}</p>
                          <p className="text-sm text-[#605A57]">{doc.date}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-[#37322F]">Logic Score</p>
                        <p className="text-lg font-semibold text-[#37322F]">{doc.score}%</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
