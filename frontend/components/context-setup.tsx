"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"

interface ContextSetupProps {
  onApply?: (context: ContextData) => void
}

interface ContextData {
  writingType: string
  goalRubrics: string[]
  keyConstraints: string[]
}

export function ContextSetup({ onApply }: ContextSetupProps) {
  const [writingType, setWritingType] = useState("Academic Essay")

  const goalRubricOptions = [
    "Clear thesis statement",
    "Logical argument flow",
    "Evidence-based support",
    "Proper citations",
    "Coherent conclusions",
  ]

  const keyConstraintOptions = [
    "Avoid passive voice",
    "Maintain formal tone",
    "Check for redundancy",
    "Verify paragraph transitions",
    "Ensure consistent terminology",
  ]

  const [selectedRubrics, setSelectedRubrics] = useState<string[]>(goalRubricOptions)
  const [selectedConstraints, setSelectedConstraints] = useState<string[]>(keyConstraintOptions)

  const handleRubricToggle = (rubric: string) => {
    setSelectedRubrics((prev) => (prev.includes(rubric) ? prev.filter((r) => r !== rubric) : [...prev, rubric]))
  }

  const handleConstraintToggle = (constraint: string) => {
    setSelectedConstraints((prev) =>
      prev.includes(constraint) ? prev.filter((c) => c !== constraint) : [...prev, constraint],
    )
  }

  const handleApply = () => {
    onApply?.({
      writingType,
      goalRubrics: selectedRubrics,
      keyConstraints: selectedConstraints,
    })
  }

  return (
    <div className="space-y-4">
      {/* Writing Type Card */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Writing Type</CardTitle>
        </CardHeader>
        <CardContent>
          <select
            value={writingType}
            onChange={(e) => setWritingType(e.target.value)}
            className="w-full p-2 border border-[rgba(55,50,47,0.12)] rounded-md text-sm bg-white text-[#37322F]"
          >
            <option>Academic Essay</option>
            <option>Research Paper</option>
            <option>Business Proposal</option>
            <option>Creative Writing</option>
          </select>
        </CardContent>
      </Card>

      {/* Goal/Rubric Checkboxes */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Goal & Rubric</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {goalRubricOptions.map((rubric) => (
            <div key={rubric} className="flex items-center gap-3">
              <Checkbox
                id={`rubric-${rubric}`}
                checked={selectedRubrics.includes(rubric)}
                onCheckedChange={() => handleRubricToggle(rubric)}
                className="border-[rgba(55,50,47,0.3)]"
              />
              <label htmlFor={`rubric-${rubric}`} className="text-sm text-[#37322F] cursor-pointer flex-1">
                {rubric}
              </label>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Key Constraints Checkboxes */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Key Constraints</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {keyConstraintOptions.map((constraint) => (
            <div key={constraint} className="flex items-center gap-3">
              <Checkbox
                id={`constraint-${constraint}`}
                checked={selectedConstraints.includes(constraint)}
                onCheckedChange={() => handleConstraintToggle(constraint)}
                className="border-[rgba(55,50,47,0.3)]"
              />
              <label htmlFor={`constraint-${constraint}`} className="text-sm text-[#37322F] cursor-pointer flex-1">
                {constraint}
              </label>
            </div>
          ))}
        </CardContent>
      </Card>

      <Button onClick={handleApply} className="w-full bg-[#37322F] hover:bg-[#37322F]/90 text-white">
        Apply Context
      </Button>
    </div>
  )
}
