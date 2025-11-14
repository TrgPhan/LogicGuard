"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { PredefinedOptionsAPI, EnhancedGoalsAPI } from "@/lib/api-service"
import type { PredefinedWritingType, GoalDetailResponse } from "@/lib/api-service"

interface ContextSetupProps {
  onApply?: (context: ContextData) => void
}

interface ContextData {
  writingType: string
  goalRubrics: string[]
  keyConstraints: string[]
  goal?: GoalDetailResponse
}

export function ContextSetup({ onApply }: ContextSetupProps) {
  const [writingTypes, setWritingTypes] = useState<PredefinedWritingType[]>([])
  const [selectedTypeId, setSelectedTypeId] = useState<string>("")
  const [selectedType, setSelectedType] = useState<PredefinedWritingType | null>(null)
  const [selectedRubrics, setSelectedRubrics] = useState<string[]>([])
  const [selectedConstraints, setSelectedConstraints] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoadingTypes, setIsLoadingTypes] = useState(true)

  // Load predefined writing types on mount
  useEffect(() => {
    async function loadWritingTypes() {
      try {
        setIsLoadingTypes(true)
        const types = await PredefinedOptionsAPI.getWritingTypes()
        setWritingTypes(types)

        if (types.length > 0) {
          const defaultType = types[0]
          setSelectedTypeId(defaultType.id)
          setSelectedType(defaultType)
          setSelectedRubrics(defaultType.default_rubrics)
          setSelectedConstraints(defaultType.default_constraints)
        }
      } catch (err) {
        setError("Failed to load writing types. Using fallback options.")
        // Fallback to hardcoded options
        const fallbackType: PredefinedWritingType = {
          id: "academic_essay",
          name: "Academic Essay",
          description: "Structured academic writing",
          default_rubrics: [
            "Clear thesis statement",
            "Logical argument flow",
            "Evidence-based support",
            "Proper citations",
            "Coherent conclusions",
          ],
          default_constraints: [
            "Avoid passive voice",
            "Maintain formal tone",
            "Check for redundancy",
            "Verify paragraph transitions",
            "Ensure consistent terminology",
          ],
        }
        setWritingTypes([fallbackType])
        setSelectedTypeId(fallbackType.id)
        setSelectedType(fallbackType)
        setSelectedRubrics(fallbackType.default_rubrics)
        setSelectedConstraints(fallbackType.default_constraints)
      } finally {
        setIsLoadingTypes(false)
      }
    }

    loadWritingTypes()
  }, [])

  // Update rubrics and constraints when writing type changes
  const handleWritingTypeChange = (typeId: string) => {
    const type = writingTypes.find((t) => t.id === typeId)
    if (type) {
      setSelectedTypeId(typeId)
      setSelectedType(type)
      setSelectedRubrics(type.default_rubrics)
      setSelectedConstraints(type.default_constraints)
    }
  }

  const handleRubricToggle = (rubric: string) => {
    setSelectedRubrics((prev) => (prev.includes(rubric) ? prev.filter((r) => r !== rubric) : [...prev, rubric]))
  }

  const handleConstraintToggle = (constraint: string) => {
    setSelectedConstraints((prev) =>
      prev.includes(constraint) ? prev.filter((c) => c !== constraint) : [...prev, constraint],
    )
  }

  const handleApply = async () => {
    if (!selectedType) return

    setLoading(true)
    setError(null)

    try {
      // Create goal with selected options
      const goal = await EnhancedGoalsAPI.create({
        writing_type_id: selectedTypeId !== "academic_essay" ? selectedTypeId : undefined,
        writing_type_custom: selectedType.name,
        selected_rubrics: selectedRubrics.length > 0 ? selectedRubrics : undefined,
        key_constraints: selectedConstraints.length > 0 ? selectedConstraints : undefined,
      })

      // Call parent callback
      onApply?.({
        writingType: selectedType.name,
        goalRubrics: selectedRubrics,
        keyConstraints: selectedConstraints,
        goal: goal,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create goal. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  if (isLoadingTypes) {
    return (
      <div className="space-y-4">
        <Card className="border-[rgba(55,50,47,0.12)]">
          <CardContent className="p-6">
            <p className="text-sm text-[#605A57]">Loading writing types...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <p className="text-sm text-red-600">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Writing Type Card */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Writing Type</CardTitle>
        </CardHeader>
        <CardContent>
          <select
            value={selectedTypeId}
            onChange={(e) => handleWritingTypeChange(e.target.value)}
            className="w-full p-2 border border-[rgba(55,50,47,0.12)] rounded-md text-sm bg-white text-[#37322F]"
            disabled={loading}
          >
            {writingTypes.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
          {selectedType && (
            <p className="mt-2 text-xs text-[#605A57]">{selectedType.description}</p>
          )}
        </CardContent>
      </Card>

      {/* Goal/Rubric Checkboxes */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Goal & Rubric</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {selectedType?.default_rubrics.map((rubric) => (
            <div key={rubric} className="flex items-center gap-3">
              <Checkbox
                id={`rubric-${rubric}`}
                checked={selectedRubrics.includes(rubric)}
                onCheckedChange={() => handleRubricToggle(rubric)}
                className="border-[rgba(55,50,47,0.3)]"
                disabled={loading}
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
          {selectedType?.default_constraints.map((constraint) => (
            <div key={constraint} className="flex items-center gap-3">
              <Checkbox
                id={`constraint-${constraint}`}
                checked={selectedConstraints.includes(constraint)}
                onCheckedChange={() => handleConstraintToggle(constraint)}
                className="border-[rgba(55,50,47,0.3)]"
                disabled={loading}
              />
              <label htmlFor={`constraint-${constraint}`} className="text-sm text-[#37322F] cursor-pointer flex-1">
                {constraint}
              </label>
            </div>
          ))}
        </CardContent>
      </Card>

      <Button
        onClick={handleApply}
        className="w-full bg-[#37322F] hover:bg-[#37322F]/90 text-white"
        disabled={loading || selectedRubrics.length === 0}
      >
        {loading ? "Creating Goal..." : "Apply Context"}
      </Button>
    </div>
  )
}
