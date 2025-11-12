/**
 * EXAMPLE: Cách refactor pages để sử dụng custom hook
 * 
 * Sau khi có useDocumentData hook, code sẽ ngắn gọn và sạch hơn nhiều
 */

// ============================================
// BEFORE (Code cũ - nhiều boilerplate)
// ============================================

/*
export default function FeedbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { selectedDocumentId } = useDocument()
  
  const [feedbackItems, setFeedbackItems] = useState<FeedbackItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const docId = searchParams.get("docId") || selectedDocumentId

  useEffect(() => {
    if (docId) {
      fetchFeedback(docId)
    }
  }, [docId])

  const fetchFeedback = async (documentId: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await FeedbackAPI.getByDocumentId(documentId)
      setFeedbackItems(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  if (!docId) {
    return <EmptyState />
  }

  if (isLoading) {
    return <Loading />
  }

  if (error) {
    return <Error message={error} />
  }

  return <FeedbackList items={feedbackItems} />
}
*/

// ============================================
// AFTER (Code mới - sử dụng hook)
// ============================================

import { useDocumentData } from "@/lib/hooks/use-document-data"
import { FeedbackAPI } from "@/lib/api-service"

export default function FeedbackPageRefactored() {
    const {
        docId,
        data: feedbackItems,
        isLoading,
        error,
        refetch
    } = useDocumentData({
        fetchFn: FeedbackAPI.getByDocumentId,
    })

    // Empty state
    if (!docId) {
        return <EmptyState />
    }

    // Loading state
    if (isLoading) {
        return <Loading />
    }

    // Error state
    if (error) {
        return <Error message={error} onRetry={refetch} />
    }

    // Main content
    return <FeedbackList items={feedbackItems || []} />
}

// ============================================
// EXAMPLE: Canvas Page với useDocumentData
// ============================================

import { DocumentsAPI } from "@/lib/api-service"
import type { Document } from "@/lib/document-context"

export default function CanvasPageRefactored() {
    const {
        docId,
        data: document,
        isLoading,
        error,
        refetch,
        setData,
    } = useDocumentData<Document>({
        fetchFn: DocumentsAPI.getById,
    })

    const [editorContent, setEditorContent] = useState("")
    const [isSaving, setIsSaving] = useState(false)

    const handleSave = async () => {
        if (!docId) return

        setIsSaving(true)
        try {
            const updated = await DocumentsAPI.update(docId, {
                content: editorContent
            })
            setData(updated) // Update local state
            // Show success toast
        } catch (err) {
            // Show error toast
        } finally {
            setIsSaving(false)
        }
    }

    if (!docId) return <EmptyState />
    if (isLoading) return <Loading />
    if (error) return <Error message={error} onRetry={refetch} />

    return (
        <div>
            <h1>{document?.title}</h1>
            <RichTextEditor
                initialContent={document?.content}
                onContentChange={setEditorContent}
            />
            <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save"}
            </Button>
        </div>
    )
}

// ============================================
// EXAMPLE: Goals Page với useDocumentData
// ============================================

import { GoalsAPI, type GoalsData } from "@/lib/api-service"

export default function GoalsPageRefactored() {
    const {
        docId,
        data: goalsData,
        isLoading,
        error,
        refetch,
    } = useDocumentData<GoalsData>({
        fetchFn: GoalsAPI.getByDocumentId,
    })

    if (!docId) return <EmptyState />
    if (isLoading) return <Loading />
    if (error) return <Error message={error} onRetry={refetch} />

    return (
        <div>
            <h1>Goal Alignment</h1>

            {/* Overall Progress */}
            <ProgressCard progress={goalsData?.overallProgress || 0} />

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 gap-4">
                {goalsData?.metrics.map((metric) => (
                    <MetricCard key={metric.name} metric={metric} />
                ))}
            </div>

            {/* Refresh Button */}
            <Button onClick={refetch}>Refresh Data</Button>
        </div>
    )
}

// ============================================
// BONUS: Custom loading states
// ============================================

export default function AdvancedExample() {
    const {
        docId,
        data,
        isLoading,
        error,
    } = useDocumentData({
        fetchFn: FeedbackAPI.getByDocumentId,
    })

    // Render different UI based on state
    return (
        <div>
            {/* No document selected */}
            {!docId && (
                <div className="text-center p-8">
                    <p>Please select a document</p>
                    <Button onClick={() => router.push("/dashboard/documents")}>
                        Go to Documents
                    </Button>
                </div>
            )}

            {/* Loading skeleton */}
            {isLoading && (
                <div className="space-y-4">
                    <Skeleton className="h-8 w-1/4" />
                    <Skeleton className="h-32 w-full" />
                    <Skeleton className="h-32 w-full" />
                </div>
            )}

            {/* Error with retry */}
            {error && (
                <div className="p-4 bg-red-50 rounded-lg">
                    <p className="text-red-600">{error}</p>
                    <Button onClick={refetch} variant="outline" className="mt-2">
                        Try Again
                    </Button>
                </div>
            )}

            {/* Success state */}
            {!isLoading && !error && data && (
                <div>
                    {/* Your content here */}
                </div>
            )}
        </div>
    )
}

// ============================================
// So sánh code:
// ============================================

/**
 * BEFORE:
 * - ~40 lines boilerplate cho mỗi page
 * - Duplicate logic ở 3 pages
 * - Khó maintain
 * 
 * AFTER:
 * - ~10 lines với hook
 * - Logic tập trung ở 1 chỗ
 * - Dễ test và maintain
 * 
 * WIN! 🎉
 */
