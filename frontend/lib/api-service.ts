import type { Document } from "./document-context"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

// Backend API Response Types (matching backend schemas)
export interface DocumentResponse {
    id: string
    user_id: string
    goal_id: string | null
    title: string
    content_full: string
    version: number
    word_count: number
    created_at: string // ISO datetime
    updated_at: string // ISO datetime
}

export interface DocumentListResponse {
    id: string
    title: string
    word_count: number
    created_at: string
    updated_at: string
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        // Handle authentication errors
        if (response.status === 401 || response.status === 403) {
            // Token expired or invalid - logout and redirect
            if (typeof window !== "undefined") {
                localStorage.removeItem("token")
                localStorage.removeItem("user")
                window.location.href = "/login?error=session_expired"
            }
            throw new Error("Authentication required. Please login again.")
        }

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

function getToken(): string | null {
    if (typeof window !== "undefined") {
        return localStorage.getItem("token")
    }
    return null
}

export const DocumentsAPI = {
    async getAll(): Promise<DocumentResponse[]> {
        const response = await fetch(`${API_BASE_URL}/documents`, {
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<DocumentResponse[]>(response)
    },

    async getById(id: string): Promise<DocumentResponse> {
        const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<DocumentResponse>(response)
    },

    async create(data: Partial<DocumentResponse>): Promise<DocumentResponse> {
        const response = await fetch(`${API_BASE_URL}/documents`, {
            method: "POST",
            headers: getHeaders(getToken() || undefined),
            body: JSON.stringify(data),
        })
        return handleResponse<DocumentResponse>(response)
    },

    async update(id: string, data: Partial<DocumentResponse>): Promise<DocumentResponse> {
        const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
            method: "PUT",
            headers: getHeaders(getToken() || undefined),
            body: JSON.stringify(data),
        })
        return handleResponse<DocumentResponse>(response)
    },

    async delete(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
            method: "DELETE",
            headers: getHeaders(getToken() || undefined),
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
            headers: getHeaders(getToken() || undefined),
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
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<GoalsData>(response)
    },
}

export const AnalysisAPI = {
    async analyze(documentId: string): Promise<{ status: string }> {
        const response = await fetch(`${API_BASE_URL}/documents/${documentId}/analyze`, {
            method: "POST",
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<{ status: string }>(response)
    },
}

// ============================================================================
// PREDEFINED OPTIONS API
// ============================================================================

export interface PredefinedWritingType {
    id: string
    name: string
    description: string
    default_rubrics: string[]
    default_constraints: string[]
}

export interface RubricTemplate {
    writing_type: string
    description: string
    rubric_items: Array<{
        label: string
        description: string
        weight: number
        is_mandatory: boolean
    }>
    constraint_items: Array<{
        label: string
        description: string
        is_required: boolean
    }>
}

export const PredefinedOptionsAPI = {
    async getWritingTypes(): Promise<PredefinedWritingType[]> {
        const response = await fetch(`${API_BASE_URL}/predefined-options/writing-types`, {
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<PredefinedWritingType[]>(response)
    },

    async getRubricTemplate(writingTypeId: string): Promise<RubricTemplate> {
        const response = await fetch(
            `${API_BASE_URL}/predefined-options/rubric-templates/${writingTypeId}`,
            {
                headers: getHeaders(getToken() || undefined),
            }
        )
        return handleResponse<RubricTemplate>(response)
    },
}

// ============================================================================
// ENHANCED GOALS API
// ============================================================================

export interface GoalCreateRequest {
    writing_type_id?: string | null
    writing_type_custom?: string | null
    rubric_text?: string
    selected_rubrics?: string[]
    key_constraints?: string[]
}

export interface GoalPreviewRequest {
    writing_type_id?: string | null
    writing_type_custom?: string | null
    rubric_text?: string
    selected_rubrics?: string[]
    key_constraints?: string[]
}

export interface CriterionPreview {
    label: string
    description: string
    weight: number
    is_mandatory: boolean
    order_index: number
}

export interface GoalPreviewResponse {
    main_goal: string
    criteria: CriterionPreview[]
    success_indicators: string[]
    writing_type: string | null
    key_constraints: string[] | null
    total_criteria: number
    mandatory_count: number
    optional_count: number
}

export interface Goal {
    id: string
    user_id: string
    writing_type_custom: string | null
    rubric_text: string
    extracted_criteria: Record<string, any>
    key_constraints: string[] | null
    created_at: string
}

export interface GoalDetailResponse extends Goal {
    criteria: Array<{
        id: string
        goal_id: string
        label: string
        description: string | null
        weight: number
        order_index: number
        is_mandatory: boolean
    }>
}

export const EnhancedGoalsAPI = {
    async create(data: GoalCreateRequest): Promise<GoalDetailResponse> {
        const response = await fetch(`${API_BASE_URL}/goals/`, {
            method: "POST",
            headers: getHeaders(getToken() || undefined),
            body: JSON.stringify(data),
        })
        return handleResponse<GoalDetailResponse>(response)
    },

    async preview(data: GoalPreviewRequest): Promise<GoalPreviewResponse> {
        const response = await fetch(`${API_BASE_URL}/goals/preview`, {
            method: "POST",
            headers: getHeaders(getToken() || undefined),
            body: JSON.stringify(data),
        })
        return handleResponse<GoalPreviewResponse>(response)
    },

    async list(): Promise<Goal[]> {
        const response = await fetch(`${API_BASE_URL}/goals/`, {
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<Goal[]>(response)
    },

    async getById(goalId: string): Promise<GoalDetailResponse> {
        const response = await fetch(`${API_BASE_URL}/goals/${goalId}`, {
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<GoalDetailResponse>(response)
    },

    async update(goalId: string, data: GoalCreateRequest): Promise<GoalDetailResponse> {
        const response = await fetch(`${API_BASE_URL}/goals/${goalId}`, {
            method: "PUT",
            headers: getHeaders(getToken() || undefined),
            body: JSON.stringify(data),
        })
        return handleResponse<GoalDetailResponse>(response)
    },

    async delete(goalId: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/goals/${goalId}`, {
            method: "DELETE",
            headers: getHeaders(getToken() || undefined),
        })
        if (!response.ok) {
            throw new Error(`Failed to delete goal: ${response.status}`)
        }
    },
}

// ============================================================================
// AUTHENTICATION API
// ============================================================================

export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    email: string
    password: string
}

export interface AuthResponse {
    access_token: string
    token_type: string
    user: {
        id: string
        email: string
        created_at: string
    }
}

export interface UserProfile {
    id: string
    email: string
    created_at: string
    total_documents?: number
    total_words_written?: number
    total_errors_found?: number
    total_errors_fixed?: number
    active_writing_time_minutes?: number
}

export const AuthAPI = {
    async login(credentials: LoginRequest): Promise<AuthResponse> {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(credentials),
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Login failed" }))
            throw new Error(error.detail || "Invalid email or password")
        }

        const data = await response.json()

        // Save token and user info to localStorage
        if (typeof window !== "undefined") {
            localStorage.setItem("token", data.access_token)
            localStorage.setItem("user", JSON.stringify(data.user))
        }

        return data
    },

    async register(credentials: RegisterRequest): Promise<AuthResponse> {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(credentials),
        })

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Registration failed" }))
            throw new Error(error.detail || "Registration failed")
        }

        const data = await response.json()

        // Auto-login after successful registration
        if (typeof window !== "undefined") {
            localStorage.setItem("token", data.access_token)
            localStorage.setItem("user", JSON.stringify(data.user))
        }

        return data
    },

    async logout(): Promise<void> {
        if (typeof window !== "undefined") {
            localStorage.removeItem("token")
            localStorage.removeItem("user")
        }
    },

    getCurrentUser(): UserProfile | null {
        if (typeof window !== "undefined") {
            const userStr = localStorage.getItem("user")
            return userStr ? JSON.parse(userStr) : null
        }
        return null
    },

    isAuthenticated(): boolean {
        return getToken() !== null
    },

    async getProfile(): Promise<UserProfile> {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: getHeaders(getToken() || undefined),
        })
        return handleResponse<UserProfile>(response)
    },
}
