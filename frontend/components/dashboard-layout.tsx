"use client"

import type React from "react"

import { DashboardHeader } from "./dashboard-header"
import { DashboardSidebar } from "./dashboard-sidebar"
import { ProtectedRoute } from "./protected-route"
import { DocumentProvider } from "@/lib/document-context"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <ProtectedRoute>
      <DocumentProvider>
        <div className="min-h-screen bg-white">
          <DashboardHeader />
          <div className="flex">
            <DashboardSidebar />
            <main className="flex-1 bg-white">{children}</main>
          </div>
        </div>
      </DocumentProvider>
    </ProtectedRoute>
  )
}
