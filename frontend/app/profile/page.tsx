"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ProtectedRoute } from "@/components/protected-route"
import { authUtils } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, User, Mail, Calendar } from "lucide-react"

export default function ProfilePage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const userData = authUtils.getUser()
    setUser(userData)
  }, [])

  const handleLogout = async () => {
    await authUtils.logout()
    router.push("/")
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#F7F5F3]">
        {/* Simple Header */}
        <header className="w-full border-b border-[rgba(55,50,47,0.12)] bg-white">
          <div className="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
            <Button variant="ghost" onClick={() => router.push("/dashboard")} className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
            <Button onClick={handleLogout} variant="outline" className="text-[#37322F] bg-transparent">
              Logout
            </Button>
          </div>
        </header>

        {/* Profile Content */}
        <main className="max-w-4xl mx-auto px-6 py-12">
          <div className="space-y-6">
            {/* Profile Header */}
            <div className="flex items-center gap-6">
              <div className="h-24 w-24 rounded-full bg-[#37322F] flex items-center justify-center">
                <User className="h-12 w-12 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-semibold text-[#37322F]">{user?.name || "User"}</h1>
                <p className="text-[#605A57] mt-1">{user?.email || ""}</p>
              </div>
            </div>

            {/* Profile Details */}
            <Card className="border-[rgba(55,50,47,0.12)]">
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Your account details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3 p-4 bg-[#F7F5F3] rounded-lg">
                  <User className="h-5 w-5 text-[#605A57]" />
                  <div>
                    <p className="text-sm font-medium text-[#605A57]">Full Name</p>
                    <p className="text-base text-[#37322F]">{user?.name || "N/A"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-[#F7F5F3] rounded-lg">
                  <Mail className="h-5 w-5 text-[#605A57]" />
                  <div>
                    <p className="text-sm font-medium text-[#605A57]">Email Address</p>
                    <p className="text-base text-[#37322F]">{user?.email || "N/A"}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-[#F7F5F3] rounded-lg">
                  <Calendar className="h-5 w-5 text-[#605A57]" />
                  <div>
                    <p className="text-sm font-medium text-[#605A57]">Member Since</p>
                    <p className="text-base text-[#37322F]">
                      {user?.createdAt
                        ? new Date(user.createdAt).toLocaleDateString("en-US", {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          })
                        : "N/A"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Links */}
            <Card className="border-[rgba(55,50,47,0.12)]">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start bg-transparent"
                  onClick={() => router.push("/dashboard")}
                >
                  Go to Dashboard
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start bg-transparent"
                  onClick={() => router.push("/dashboard/settings")}
                >
                  Edit Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
