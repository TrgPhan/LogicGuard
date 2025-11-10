"use client"

import type React from "react"
import { DocumentProvider } from "@/lib/document-context"
import { DashboardLayout } from "@/components/dashboard-layout"

export default function DashboardPageLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <DocumentProvider>
      <DashboardLayout>{children}</DashboardLayout>
    </DocumentProvider>
  )
}
