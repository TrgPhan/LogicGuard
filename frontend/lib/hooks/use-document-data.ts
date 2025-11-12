/**
 * Custom Hook để fetch document data
 * Tái sử dụng logic chung cho Canvas, Feedback, Goals pages
 */

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { useDocument } from "../document-context"

interface UseDocumentDataOptions<T> {
    /**
     * Function để fetch data từ API
     * Nhận vào documentId và trả về Promise<T>
     */
    fetchFn: (documentId: string) => Promise<T>

    /**
     * Initial data (optional)
     */
    initialData?: T

    /**
     * Có auto-fetch khi component mount không (default: true)
     */
    autoFetch?: boolean
}

interface UseDocumentDataReturn<T> {
    /**
     * Document ID hiện tại (từ URL hoặc context)
     */
    docId: string | null

    /**
     * Data đã fetch
     */
    data: T | null

    /**
     * Loading state
     */
    isLoading: boolean

    /**
     * Error message nếu có
     */
    error: string | null

    /**
     * Function để refetch data
     */
    refetch: () => Promise<void>

    /**
     * Function để set data manually
     */
    setData: React.Dispatch<React.SetStateAction<T | null>>
}

/**
 * Hook để fetch data theo document ID
 * 
 * @example
 * ```typescript
 * const { docId, data, isLoading, error } = useDocumentData({
 *   fetchFn: (id) => FeedbackAPI.getByDocumentId(id)
 * })
 * ```
 */
export function useDocumentData<T>({
    fetchFn,
    initialData,
    autoFetch = true,
}: UseDocumentDataOptions<T>): UseDocumentDataReturn<T> {
    const searchParams = useSearchParams()
    const { selectedDocumentId } = useDocument()

    // Get docId from URL hoặc context
    const docId = searchParams.get("docId") || selectedDocumentId

    const [data, setData] = useState<T | null>(initialData || null)
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const fetchData = async () => {
        if (!docId) return

        setIsLoading(true)
        setError(null)

        try {
            const result = await fetchFn(docId)
            setData(result)
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "An error occurred"
            setError(errorMessage)
            console.error("Failed to fetch document data:", err)
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        if (autoFetch && docId) {
            fetchData()
        }
    }, [docId, autoFetch])

    return {
        docId,
        data,
        isLoading,
        error,
        refetch: fetchData,
        setData,
    }
}
