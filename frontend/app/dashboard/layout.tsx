"use client"

import type React from "react"
import { DocumentProvider } from "@/lib/document-context"
import { DashboardLayout } from "@/components/dashboard-layout"
import { ProtectedRoute } from "@/components/protected-route"

export default function DashboardPageLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ProtectedRoute>
      <DocumentProvider>
        <DashboardLayout>{children}</DashboardLayout>
      </DocumentProvider>
    </ProtectedRoute>
  )
}
