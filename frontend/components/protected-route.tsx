"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { authUtils } from "@/lib/auth"

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      const authenticated = authUtils.isAuthenticated()

      if (!authenticated) {
        router.push("/login")
        return
      }

      // Verify token is still valid
      const profile = await authUtils.getProfile()
      if (!profile.success) {
        authUtils.removeToken()
        router.push("/login")
        return
      }

      setIsAuthenticated(true)
      setIsLoading(false)
    }

    checkAuth()
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F7F5F3]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#37322F] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#605A57]">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
