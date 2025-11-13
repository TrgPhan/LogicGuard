"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { useRouter, usePathname } from "next/navigation"
import { AuthAPI } from "@/lib/api-service"

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      // Check if token exists
      const authenticated = AuthAPI.isAuthenticated()

      if (!authenticated) {
        // Save current path to redirect back after login
        if (typeof window !== "undefined") {
          sessionStorage.setItem("redirectAfterLogin", pathname)
        }
        router.push("/login")
        return
      }

      // Verify token is still valid by fetching profile
      try {
        await AuthAPI.getProfile()
        setIsAuthenticated(true)
      } catch (error) {
        // Token invalid or expired
        console.error("Auth check failed:", error)
        AuthAPI.logout()
        if (typeof window !== "undefined") {
          sessionStorage.setItem("redirectAfterLogin", pathname)
        }
        router.push("/login?error=session_expired")
        return
      }

      setIsLoading(false)
    }

    checkAuth()
  }, [router, pathname])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F7F5F3]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#37322F] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#605A57]">Checking authentication...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
