"use client"

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface AnalysisIssue {
    id: string
    type: "logic_contradiction" | "logic_gap" | "weak_evidence" | "clarity_issue"
    startPos: number
    endPos: number
    suggestion?: string
    message: string
    text?: string
}

interface AnalysisIssueProps {
    issue: AnalysisIssue
    onApply: () => void
}

const issueTypeLabels: Record<AnalysisIssue["type"], string> = {
    logic_contradiction: "Logic Contradiction",
    logic_gap: "Logic Gap",
    weak_evidence: "Weak Evidence",
    clarity_issue: "Clarity Issue",
}

export function AnalysisIssueHighlight({ issue, onApply }: AnalysisIssueProps) {
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <span
                        className="bg-red-200 text-red-900 underline decoration-red-500 cursor-help"
                        onClick={onApply}
                    >
                        {/* Text will be highlighted by parent */}
                    </span>
                </TooltipTrigger>
                <TooltipContent side="top" className="max-w-xs">
                    <div className="space-y-2">
                        <p className="font-semibold text-sm">{issueTypeLabels[issue.type]}</p>
                        <p className="text-xs text-gray-100">{issue.suggestion}</p>
                        <p className="text-xs text-gray-200 italic">Click to apply suggestion</p>
                    </div>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    )
}
