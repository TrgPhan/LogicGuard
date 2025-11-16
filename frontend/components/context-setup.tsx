"use client"

import { useState, useEffect, useMemo, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { PredefinedOptionsAPI, EnhancedGoalsAPI } from "@/lib/api-service"
import type { PredefinedWritingType, GoalDetailResponse } from "@/lib/api-service"

const DEFAULT_WRITING_TYPES: PredefinedWritingType[] = [
  {
    id: "academic_essay",
    name: "Academic Essay",
    description: "Structured academic writing with thesis and evidence",
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
  },
  {
    id: "research_paper",
    name: "Research Paper",
    description: "In-depth research with methodology and findings",
    default_rubrics: [
      "Clear research question",
      "Comprehensive literature review",
      "Sound methodology",
      "Valid data analysis",
      "Meaningful conclusions",
    ],
    default_constraints: [
      "Use academic language",
      "Cite all sources properly",
      "Follow format guidelines",
      "Maintain objectivity",
      "Support claims with evidence",
    ],
  },
  {
    id: "business_proposal",
    name: "Business Proposal",
    description: "Professional business proposal with problem-solution structure",
    default_rubrics: [
      "Clear problem statement",
      "Feasible solution",
      "Cost-benefit analysis",
      "Implementation timeline",
      "Risk assessment",
    ],
    default_constraints: [
      "Use professional language",
      "Include supporting data",
      "Address stakeholder concerns",
      "Provide clear recommendations",
      "Follow business format",
    ],
  },
  {
    id: "creative_writing",
    name: "Creative Writing",
    description: "Creative narrative with engaging storytelling",
    default_rubrics: [
      "Engaging narrative voice",
      "Strong character development",
      "Vivid descriptions",
      "Compelling plot structure",
      "Emotional resonance",
    ],
    default_constraints: [
      "Show, don't tell",
      "Maintain consistent point of view",
      "Use active voice",
      "Create sensory details",
      "Develop authentic dialogue",
    ],
  },
]

interface ContextSetupProps {
  goal?: GoalDetailResponse | null
  onApply?: (context: ContextData) => void
}

interface ContextData {
  writingType: string
  goalRubrics: string[]
  keyConstraints: string[]
  goal: GoalDetailResponse
}

const parseRubricText = (text?: string | null): string[] => {
  if (!text) return []
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => line.replace(/^(?:\d+[\.)]|[-•])\s*/, ""))
}

export function ContextSetup({ goal, onApply }: ContextSetupProps) {
  const [writingTypes, setWritingTypes] = useState<PredefinedWritingType[]>([])
  const [selectedTypeId, setSelectedTypeId] = useState<string>("")
  const [selectedType, setSelectedType] = useState<PredefinedWritingType | null>(null)
  const [persistedWritingTypeName, setPersistedWritingTypeName] = useState<string>("")
  const [selectedRubrics, setSelectedRubrics] = useState<string[]>([])
  const [selectedConstraints, setSelectedConstraints] = useState<string[]>([])
  const [typeSelections, setTypeSelections] = useState<Record<string, { rubrics: string[]; constraints: string[] }>>({})
  const [currentGoal, setCurrentGoal] = useState<GoalDetailResponse | null>(goal ?? null)
  const [hydratedGoalVersion, setHydratedGoalVersion] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [isLoadingTypes, setIsLoadingTypes] = useState(true)

  useEffect(() => {
    setCurrentGoal(goal ?? null)
    setHydratedGoalVersion(null)
  }, [goal?.id])

  useEffect(() => {
    async function loadWritingTypes() {
      try {
        setIsLoadingTypes(true)
        const types = await PredefinedOptionsAPI.getWritingTypes()
        setWritingTypes(types.length ? types : DEFAULT_WRITING_TYPES)
      } catch (err) {
        setError("Failed to load writing types. Using fallback options.")
        setWritingTypes(DEFAULT_WRITING_TYPES)
      } finally {
        setIsLoadingTypes(false)
      }
    }

    loadWritingTypes()
  }, [])

  const hydrateFromGoal = useCallback(
    (goalData: GoalDetailResponse) => {
      const resolvedType = (() => {
        if (goalData.writing_type_id) {
          return writingTypes.find((t) => t.id === goalData.writing_type_id) ?? null
        }
        if (goalData.writing_type_custom) {
          const normalized = goalData.writing_type_custom.toLowerCase()
          return (
            writingTypes.find((t) => t.id === goalData.writing_type_custom) ??
            writingTypes.find((t) => t.name.toLowerCase() === normalized) ??
            null
          )
        }
        return null
      })()

      if (resolvedType) {
        setSelectedTypeId(resolvedType.id)
        setSelectedType(resolvedType)
      } else if (writingTypes.length > 0) {
        const fallbackType = writingTypes[0]
        setSelectedTypeId(fallbackType.id)
        setSelectedType(fallbackType)
      }

      const resolvedName = resolvedType?.name || goalData.writing_type_custom || ""
      setPersistedWritingTypeName(resolvedName)

      const rubricValues = goalData.criteria?.length
        ? goalData.criteria.map((c) => c.label)
        : parseRubricText(goalData.rubric_text)

      const hydratedRubrics = rubricValues.length ? rubricValues : resolvedType?.default_rubrics ?? []
      const hydratedConstraints = goalData.key_constraints ?? resolvedType?.default_constraints ?? []

      setSelectedRubrics(hydratedRubrics)
      setSelectedConstraints(hydratedConstraints)
      const key = resolvedType?.id || resolvedName || "default"
      if (key) {
        setTypeSelections((prev) => ({
          ...prev,
          [key]: {
            rubrics: hydratedRubrics,
            constraints: hydratedConstraints,
          },
        }))
      }
    },
    [writingTypes]
  )

  useEffect(() => {
    if (isLoadingTypes || !currentGoal) {
      return
    }

    const versionKey = `${currentGoal.id}:${currentGoal.updated_at ?? ""}:${currentGoal.writing_type_id ?? ""}:${currentGoal.writing_type_custom ?? ""}`
    if (hydratedGoalVersion === versionKey) {
      return
    }

    hydrateFromGoal(currentGoal)
    setHydratedGoalVersion(versionKey)
  }, [currentGoal, hydrateFromGoal, hydratedGoalVersion, isLoadingTypes])

  useEffect(() => {
    if (isLoadingTypes || currentGoal || selectedTypeId || writingTypes.length === 0) {
      return
    }

    const defaultType = writingTypes[0]
    setSelectedType(defaultType)
    setSelectedTypeId(defaultType.id)
    setPersistedWritingTypeName(defaultType.name)
    setSelectedRubrics(defaultType.default_rubrics)
    setSelectedConstraints(defaultType.default_constraints)
    setTypeSelections((prev) => ({
      ...prev,
      [defaultType.id]: {
        rubrics: defaultType.default_rubrics,
        constraints: defaultType.default_constraints,
      },
    }))
  }, [currentGoal, isLoadingTypes, selectedTypeId, writingTypes])

  const handleWritingTypeChange = (typeId: string) => {
    setStatusMessage(null)
    const currentKey = selectedTypeId || persistedWritingTypeName || "default"
    if (currentKey) {
      setTypeSelections((prev) => ({
        ...prev,
        [currentKey]: {
          rubrics: selectedRubrics,
          constraints: selectedConstraints,
        },
      }))
    }

    if (!typeId) {
      setSelectedTypeId("")
      setSelectedType(null)
      setPersistedWritingTypeName("")
      setSelectedRubrics([])
      setSelectedConstraints([])
      return
    }

    const type = writingTypes.find((t) => t.id === typeId)
    if (type) {
      setSelectedTypeId(typeId)
      setSelectedType(type)
      setPersistedWritingTypeName(type.name)
      const cachedSelection = typeSelections[type.id]
      const nextRubrics = cachedSelection?.rubrics ?? type.default_rubrics
      const nextConstraints = cachedSelection?.constraints ?? type.default_constraints
      setSelectedRubrics(nextRubrics)
      setSelectedConstraints(nextConstraints)
      setTypeSelections((prev) => ({
        ...prev,
        [type.id]: {
          rubrics: nextRubrics,
          constraints: nextConstraints,
        },
      }))
    }
  }

  const handleRubricToggle = (rubric: string) => {
    setSelectedRubrics((prev) => {
      const next = prev.includes(rubric) ? prev.filter((r) => r !== rubric) : [...prev, rubric]
      const key = selectedTypeId || persistedWritingTypeName || "default"
      if (key) {
        setTypeSelections((prevSelections) => ({
          ...prevSelections,
          [key]: {
            rubrics: next,
            constraints: prevSelections[key]?.constraints ?? selectedConstraints,
          },
        }))
      }
      return next
    })
  }

  const handleConstraintToggle = (constraint: string) => {
    setSelectedConstraints((prev) => {
      const next = prev.includes(constraint) ? prev.filter((c) => c !== constraint) : [...prev, constraint]
      const key = selectedTypeId || persistedWritingTypeName || "default"
      if (key) {
        setTypeSelections((prevSelections) => ({
          ...prevSelections,
          [key]: {
            rubrics: prevSelections[key]?.rubrics ?? selectedRubrics,
            constraints: next,
          },
        }))
      }
      return next
    })
  }

  const rubricOptions = useMemo(() => {
    const defaults = selectedType?.default_rubrics ?? []
    return Array.from(new Set([...defaults, ...selectedRubrics]))
  }, [selectedRubrics, selectedType])

  const constraintOptions = useMemo(() => {
    const defaults = selectedType?.default_constraints ?? []
    return Array.from(new Set([...defaults, ...selectedConstraints]))
  }, [selectedConstraints, selectedType])

  const isUuid = (value: string) => /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/.test(value)

  const handleApply = async () => {
    setError(null)
    setStatusMessage(null)

    if (selectedRubrics.length === 0) {
      setError("Select at least one rubric item.")
      return
    }

    setLoading(true)

    try {
      const maybeUuid = selectedTypeId && isUuid(selectedTypeId)
      const writingTypeId = maybeUuid ? selectedTypeId : undefined
      const writingTypeLabel = selectedType?.name || persistedWritingTypeName || currentGoal?.writing_type_custom || "Goal"
      const writingTypeCustomValue = selectedTypeId && !maybeUuid ? selectedTypeId : writingTypeLabel

      const payload = {
        writing_type_id: writingTypeId,
        writing_type_custom: writingTypeCustomValue,
        selected_rubrics: selectedRubrics,
        key_constraints: selectedConstraints,
        rubric_text: selectedRubrics.map((item, idx) => `${idx + 1}. ${item}`).join("\n"),
      }

      const savedGoal = currentGoal
        ? await EnhancedGoalsAPI.update(currentGoal.id, payload)
        : await EnhancedGoalsAPI.create(payload)

      setCurrentGoal(savedGoal)
      setHydratedGoalVersion(null)
      setPersistedWritingTypeName(writingTypeLabel)
      setStatusMessage(currentGoal ? "Goal updated successfully." : "Goal created and linked.")

      onApply?.({
        writingType: writingTypeLabel,
        goalRubrics: selectedRubrics,
        keyConstraints: selectedConstraints,
        goal: savedGoal,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save goal. Please try again.")
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

      {statusMessage && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="p-4">
            <p className="text-sm text-green-700">{statusMessage}</p>
          </CardContent>
        </Card>
      )}

      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Writing Type</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <select
            value={selectedTypeId}
            onChange={(e) => handleWritingTypeChange(e.target.value)}
            className="w-full p-2 border border-[rgba(55,50,47,0.12)] rounded-md text-sm bg-white text-[#37322F]"
            disabled={loading}
          >
            <option value="">Select a writing type</option>
            {writingTypes.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
          {selectedType && <p className="text-xs text-[#605A57]">{selectedType.description}</p>}
        </CardContent>
      </Card>

      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Goal & Rubric</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {rubricOptions.length === 0 && <p className="text-sm text-[#605A57]">No rubric items available.</p>}
          {rubricOptions.map((rubric) => (
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

      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle className="text-base">Key Constraints</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {constraintOptions.length === 0 && (
            <p className="text-sm text-[#605A57]">No constraints defined for this writing type.</p>
          )}
          {constraintOptions.map((constraint) => (
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
        disabled={loading || selectedRubrics.length === 0 || !selectedTypeId}
      >
        {loading ? "Saving..." : currentGoal ? "Update Goal" : "Apply Context"}
      </Button>
    </div>
  )
}
