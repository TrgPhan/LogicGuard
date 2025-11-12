"use client"

import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { cn } from "@/lib/utils"
import { PenTool, MessageSquare, Target, Settings, FileText, LayoutGrid } from "lucide-react"
import { useDocument } from "@/lib/document-context"

const navigation = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutGrid,
  },
]

const mainStack = {
  name: "Documents",
  href: "/dashboard/documents",
  icon: FileText,
}

const subStacks = [
  {
    name: "Writing Canvas",
    href: "/dashboard/canvas",
    icon: PenTool,
    requiresDocument: true,
  },
  {
    name: "Feedback",
    href: "/dashboard/feedback",
    icon: MessageSquare,
    requiresDocument: true,
  },
  {
    name: "Goal Alignment",
    href: "/dashboard/goals",
    icon: Target,
    requiresDocument: true,
  },
]

const otherNavigation = [
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
]

export function DashboardSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const searchParams = useSearchParams()
  const { selectedDocumentId, selectedDocument } = useDocument()

  const handleNavigation = (href: string, requiresDocument = false) => {
    if (requiresDocument && selectedDocumentId) {
      const params = new URLSearchParams()
      params.set("docId", selectedDocumentId)
      router.push(`${href}?${params.toString()}`)
    } else if (requiresDocument && !selectedDocumentId) {
      router.push(href)
    } else {
      router.push(href)
    }
  }

  return (
    <aside className="w-64 border-r border-[rgba(55,50,47,0.12)] bg-[#F7F5F3] min-h-[calc(100vh-73px)] sticky top-[73px]">
      <nav className="p-4 space-y-0.5">
        <div className="mb-4">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <button
                key={item.name}
                onClick={() => handleNavigation(item.href)}
                className={cn(
                  "w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors text-left",
                  isActive ? "bg-[#37322F] text-white" : "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F]",
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </button>
            )
          })}
        </div>

        <div className="mb-4">
          <button
            onClick={() => handleNavigation(mainStack.href)}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors text-left",
              pathname === mainStack.href
                ? "bg-[#37322F] text-white"
                : "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F]",
            )}
          >
            {(() => {
              const Icon = mainStack.icon
              return <Icon className="h-5 w-5" />
            })()}
            {mainStack.name}
          </button>

          <div className="mt-0.5 space-y-0.5 pl-4 border-l-2 border-[rgba(55,50,47,0.12)] ml-2">
            {subStacks.map((item) => {
              const isActive = pathname === item.href
              const hasDocument = !!selectedDocumentId
              const Icon = item.icon

              return (
                <button
                  key={item.name}
                  onClick={() => handleNavigation(item.href, item.requiresDocument)}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-all text-left",
                    isActive
                      ? "bg-[#37322F] text-white font-bold"
                      : hasDocument
                        ? "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F] font-medium"
                        : "text-[#A19C99] hover:bg-[#E8E6E3] hover:text-[#605A57] font-medium",
                  )}
                  title={!hasDocument ? "Select a document first" : undefined}
                >
                  <Icon className="h-4 w-4" />
                  <span className="flex-1">{item.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        <div>
          {otherNavigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <button
                key={item.name}
                onClick={() => handleNavigation(item.href)}
                className={cn(
                  "w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors text-left",
                  isActive ? "bg-[#37322F] text-white" : "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F]",
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </button>
            )
          })}
        </div>

        {selectedDocument && (
          <div className="mt-4 p-3 bg-white rounded-lg border border-[rgba(55,50,47,0.12)]">
            <p className="text-xs text-[#605A57] mb-1">Current Document</p>
            <p className="text-sm font-medium text-[#37322F] truncate" title={selectedDocument.title}>
              {selectedDocument.title}
            </p>
            {selectedDocument.score && (
              <p className="text-xs text-[#605A57] mt-1">Score: {selectedDocument.score}%</p>
            )}
          </div>
        )}
      </nav>
    </aside>
  )
}
