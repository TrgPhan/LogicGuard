"use client"

import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PenTool, Save, Download } from "lucide-react"

export default function CanvasPage() {
  return (
    <DashboardLayout>
      <div className="p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Writing Canvas</h1>
            <p className="text-[#605A57]">Start writing with real-time logic checking</p>
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
          {/* Editor Area */}
          <div className="lg:col-span-2">
            <Card className="border-[rgba(55,50,47,0.12)] min-h-[600px]">
              <CardHeader className="border-b border-[rgba(55,50,47,0.12)]">
                <CardTitle className="text-lg">Document Editor</CardTitle>
                <CardDescription>TipTap editor will be integrated here</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="min-h-[500px] p-4 bg-white rounded border border-[rgba(55,50,47,0.12)] focus-within:ring-2 focus-within:ring-[#37322F]/20">
                  <p className="text-[#605A57] italic">Start typing your content here...</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Context Setup Panel */}
          <div className="space-y-4">
            <Card className="border-[rgba(55,50,47,0.12)]">
              <CardHeader>
                <CardTitle className="text-lg">Context Setup</CardTitle>
                <CardDescription>Define your writing parameters</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-[#37322F] mb-2 block">Writing Type</label>
                  <select className="w-full p-2 border border-[rgba(55,50,47,0.12)] rounded-md text-sm">
                    <option>Academic Essay</option>
                    <option>Research Paper</option>
                    <option>Business Proposal</option>
                    <option>Creative Writing</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-[#37322F] mb-2 block">Goal/Rubric</label>
                  <textarea
                    className="w-full p-2 border border-[rgba(55,50,47,0.12)] rounded-md text-sm min-h-[80px]"
                    placeholder="Describe your writing goals..."
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-[#37322F] mb-2 block">Key Constraints</label>
                  <textarea
                    className="w-full p-2 border border-[rgba(55,50,47,0.12)] rounded-md text-sm min-h-[60px]"
                    placeholder="Any specific requirements..."
                  />
                </div>
                <Button className="w-full bg-[#37322F] hover:bg-[#37322F]/90">Apply Context</Button>
              </CardContent>
            </Card>

            <Card className="border-[rgba(55,50,47,0.12)]">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <PenTool className="h-5 w-5" />
                  Writing Stats
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-[#605A57]">Words</span>
                  <span className="text-sm font-medium text-[#37322F]">0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#605A57]">Characters</span>
                  <span className="text-sm font-medium text-[#37322F]">0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#605A57]">Logic Issues</span>
                  <span className="text-sm font-medium text-[#37322F]">0</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
