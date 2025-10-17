"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { LayoutDashboard, PenTool, MessageSquare, Target, Settings, FileText } from "lucide-react"

const navigation = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
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
  {
    name: "Documents",
    href: "/dashboard/documents",
    icon: FileText,
  },
  {
    name: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
]

export function DashboardSidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 border-r border-[rgba(55,50,47,0.12)] bg-[#F7F5F3] min-h-[calc(100vh-73px)] sticky top-[73px]">
      <nav className="p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors",
                isActive ? "bg-[#37322F] text-white" : "text-[#605A57] hover:bg-[#E8E6E3] hover:text-[#37322F]",
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
