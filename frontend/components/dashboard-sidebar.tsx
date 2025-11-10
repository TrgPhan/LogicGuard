"use client"

import { usePathname, useRouter } from "next/navigation"
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
  },
  {
    name: "Feedback",
    href: "/dashboard/feedback",
    icon: MessageSquare,
  },
  {
    name: "Goal Alignment",
    href: "/dashboard/goals",
    icon: Target,
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
  const { selectedDocumentId } = useDocument()

  const handleSubStackClick = (href: string) => {
    if (!selectedDocumentId) {
      router.push("/dashboard/documents")
      setTimeout(() => {
        const documentsSection = document.querySelector("[data-section='documents']")
        if (documentsSection) {
          documentsSection.scrollIntoView({ behavior: "smooth" })
        }
      }, 100)
    } else {
      router.push(href)
    }
  }

  return (
    <aside className="w-64 border-r border-[rgba(55,50,47,0.12)] bg-[#F7F5F3] min-h-[calc(100vh-73px)] sticky top-[73px]">
      <nav className="p-4 space-y-1">
        {/* Overview section */}
        <div className="mb-6">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <button
                key={item.name}
                onClick={() => router.push(item.href)}
                className={cn(
                  "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors text-left",
                  isActive ? "bg-[#37322F] text-white" : "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F]",
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </button>
            )
          })}
        </div>

        {/* Documents with nested sub-stacks */}
        <div className="mb-6">
          {/* Main Documents Link */}
          <button
            onClick={() => router.push(mainStack.href)}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors text-left",
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

          <div className="mt-1 space-y-1 pl-4 border-l-2 border-[rgba(55,50,47,0.12)] ml-2">
            {subStacks.map((item) => {
              const isActive = pathname === item.href
              const isDisabled = !selectedDocumentId
              const Icon = item.icon

              return (
                <button
                  key={item.name}
                  onClick={() => handleSubStackClick(item.href)}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-all text-left",
                    isDisabled
                      ? "text-[#D4CCCB] cursor-not-allowed opacity-60 font-medium"
                      : isActive
                        ? "bg-[#37322F] text-white font-bold"
                        : "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F] font-medium",
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="flex-1">{item.name}</span>
                  {isDisabled && <span className="text-xs opacity-70">🔒</span>}
                </button>
              )
            })}
          </div>
        </div>

        {/* Other Navigation */}
        <div>
          {otherNavigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon

            return (
              <button
                key={item.name}
                onClick={() => router.push(item.href)}
                className={cn(
                  "w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors text-left",
                  isActive ? "bg-[#37322F] text-white" : "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F]",
                )}
              >
                <Icon className="h-5 w-5" />
                {item.name}
              </button>
            )
          })}
        </div>
      </nav>
    </aside>
  )
}
