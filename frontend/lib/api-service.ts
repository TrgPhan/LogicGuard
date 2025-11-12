import type { Document } from "./document-context"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: "An error occurred" }))
        throw new Error(error.message || `HTTP error! status: ${response.status}`)
    }
    return response.json()
}

function getHeaders(token?: string): HeadersInit {
    const headers: HeadersInit = {
        "Content-Type": "application/json",
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`
    }

    return headers
}

export const DocumentsAPI = {
    async getAll(): Promise<Document[]> {
        const response = await fetch(`${API_BASE_URL}/documents`, {
            headers: getHeaders(),
        })
        return handleResponse<Document[]>(response)
    },

    async getById(id: string): Promise<Document> {
        const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
            headers: getHeaders(),
        })
        return handleResponse<Document>(response)
    },

    async create(data: Partial<Document>): Promise<Document> {
        const response = await fetch(`${API_BASE_URL}/documents`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify(data),
        })
        return handleResponse<Document>(response)
    },

    async update(id: string, data: Partial<Document>): Promise<Document> {
        const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify(data),
        })
        return handleResponse<Document>(response)
    },

    async delete(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
            method: "DELETE",
            headers: getHeaders(),
        })
        return handleResponse<void>(response)
    },
}

export interface FeedbackItem {
    severity: "high" | "medium" | "low"
    type: string
    message: string
    location: string
    suggestion: string
}

export const FeedbackAPI = {
    async getByDocumentId(documentId: string): Promise<FeedbackItem[]> {
        const response = await fetch(`${API_BASE_URL}/documents/${documentId}/feedback`, {
            headers: getHeaders(),
        })
        return handleResponse<FeedbackItem[]>(response)
    },
}

export interface GoalMetric {
    name: string
    value: number
    target: number
    status: "excellent" | "good" | "warning" | "poor"
}

export interface GoalsData {
    metrics: GoalMetric[]
    overallProgress: number
}

export const GoalsAPI = {
    async getByDocumentId(documentId: string): Promise<GoalsData> {
        const response = await fetch(`${API_BASE_URL}/documents/${documentId}/goals`, {
            headers: getHeaders(),
        })
        return handleResponse<GoalsData>(response)
    },
}

export const AnalysisAPI = {
    async analyze(documentId: string): Promise<{ status: string }> {
        const response = await fetch(`${API_BASE_URL}/documents/${documentId}/analyze`, {
            method: "POST",
            headers: getHeaders(),
        })
        return handleResponse<{ status: string }>(response)
    },
}
