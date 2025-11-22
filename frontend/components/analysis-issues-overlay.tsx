"use client"

import { Card } from "@/components/ui/card"
import { AnalysisIssue } from "@/components/rich-text-editor"

interface AnalysisIssuesOverlayProps {
  issues: AnalysisIssue[]
  onSuggestionClick: (issue: AnalysisIssue) => void
}

const issueTypeLabels: Record<AnalysisIssue["type"], string> = {
  logic_contradiction: "Logic Contradiction",
  logic_gap: "Logic Gap",
  weak_evidence: "Weak Evidence",
  clarity_issue: "Clarity Issue",
  undefined_term: "Undefined Term",
}

export function AnalysisIssuesOverlay({ issues, onSuggestionClick }: AnalysisIssuesOverlayProps) {
  if (issues.length === 0) return null

  return (
    <Card className="bg-[#F7F5F3] border-[rgba(55,50,47,0.12)] p-4 space-y-3 sticky top-0">
      <h3 className="font-bold text-[#37322F] text-sm">Issues Found</h3>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {issues.map(issue => (
          <button
            key={issue.id}
            type="button"
            className="w-full text-left bg-white p-3 rounded border border-[rgba(55,50,47,0.12)] hover:bg-[#FAF9F7] transition-colors"
            onClick={() => onSuggestionClick(issue)}
          >
            <div className="flex items-start gap-2">
              <span className="inline-block px-2 py-0.5 text-xs font-semibold bg-red-100 text-red-700 rounded">
                {issueTypeLabels[issue.type]}
              </span>
            </div>
            <p className="text-xs text-[#37322F] mt-2">
              <span className="text-red-700 font-semibold">{issue.text}</span>
            </p>
            {issue.suggestion && (
              <p className="text-xs text-green-700 mt-2">
                Suggestion: <span className="font-semibold text-green-700">{issue.suggestion}</span>
              </p>
            )}
            <p className="text-xs text-[#605A57] mt-2">{issue.message}</p>
          </button>
        ))}
      </div>
    </Card>
  )
}
