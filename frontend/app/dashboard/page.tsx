"use client"

import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PenTool, MessageSquare, Target, FileText, TrendingUp, CheckCircle2, Loader2 } from "lucide-react"
import { useDocument } from "@/lib/document-context"
import { DocumentsAPI, AuthAPI } from "@/lib/api-service"
import { formatDistanceToNow } from "date-fns"

export default function DashboardPage() {
  const router = useRouter()
  const { setSelectedDocumentId } = useDocument()
  const [recentDocs, setRecentDocs] = useState<any[]>([])
  const [stats, setStats] = useState({
    totalDocs: 0,
    totalWords: 0,
    avgScore: 0,
    issuesFound: 0,
  })
  const [isLoading, setIsLoading] = useState(true)
  const [userName, setUserName] = useState("User")

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setIsLoading(true)
    try {
      // Fetch user profile
      const profile = await AuthAPI.getProfile()
      setUserName(profile.email.split('@')[0])

      // Fetch documents
      const docs = await DocumentsAPI.getAll()
      
      // Calculate stats
      const totalWords = docs.reduce((sum, doc) => sum + (doc.word_count || 0), 0)
      
      // Get recent 3 documents
      const sortedDocs = docs
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, 3)
        .map(doc => ({
          id: doc.id,
          title: doc.title,
          date: formatDistanceToNow(new Date(doc.updated_at), { addSuffix: true }),
          words: doc.word_count,
        }))

      setRecentDocs(sortedDocs)
      setStats({
        totalDocs: docs.length,
        totalWords,
        avgScore: 0, // Will be available when Analysis API is ready
        issuesFound: 0, // Will be available when Feedback API is ready
      })
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRecentDocumentClick = (docId: string) => {
    setSelectedDocumentId(docId)
    const params = new URLSearchParams()
    params.set("docId", docId)
    router.push(`/dashboard/canvas?${params.toString()}`)
  }

  if (isLoading) {
    return (
      <div className="p-8 flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-[#37322F]" />
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Welcome back, {userName}!</h1>
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
            <div className="text-2xl font-bold text-[#37322F]">{stats.totalDocs}</div>
            <p className="text-xs text-[#605A57] mt-1">All your documents</p>
          </CardContent>
        </Card>

        <Card className="border-[rgba(55,50,47,0.12)]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-[#605A57]">Total Words</CardTitle>
            <TrendingUp className="h-4 w-4 text-[#605A57]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#37322F]">{stats.totalWords.toLocaleString()}</div>
            <p className="text-xs text-[#605A57] mt-1">Across all documents</p>
          </CardContent>
        </Card>

        <Card className="border-[rgba(55,50,47,0.12)]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-[#605A57]">Issues Found</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-[#605A57]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#37322F]">{stats.issuesFound}</div>
            <p className="text-xs text-[#605A57] mt-1">Awaiting Analysis API</p>
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
            {recentDocs.length === 0 ? (
              <div className="p-8 text-center text-[#605A57]">
                No documents yet. Create your first one!
              </div>
            ) : (
              <div className="divide-y divide-[rgba(55,50,47,0.12)]">
                {recentDocs.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => handleRecentDocumentClick(doc.id)}
                    className="p-4 hover:bg-[#F7F5F3] cursor-pointer transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-[#605A57]" />
                        <div>
                          <p className="font-medium text-[#37322F]">{doc.title}</p>
                          <p className="text-sm text-[#605A57]">{doc.date}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-[#605A57]">{doc.words} words</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
