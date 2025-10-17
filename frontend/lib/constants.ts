export interface User {
  id: string
  email: string
  password: string // In production, this would never be stored client-side
  name: string
  createdAt: string
}

export interface AuthResponse {
  success: boolean
  token?: string
  user?: Omit<User, "password">
  message?: string
}

export interface ProfileResponse {
  success: boolean
  user?: Omit<User, "password">
  message?: string
}

// ============================================================================
// API ENDPOINTS - Replace these with your FastAPI URLs
// ============================================================================

export const API_ENDPOINTS = {
  login: "/api/auth/login",
  register: "/api/auth/register",
  profile: "/api/auth/profile",
  logout: "/api/auth/logout",
  // Add more endpoints as needed
}

// ============================================================================
// MOCK DATA
// ============================================================================

export const MOCK_USERS: User[] = [
  {
    id: "1",
    email: "demo@logicguard.com",
    password: "password123",
    name: "Demo User",
    createdAt: new Date().toISOString(),
  },
  {
    id: "2",
    email: "test@example.com",
    password: "test123",
    name: "Test User",
    createdAt: new Date().toISOString(),
  },
]

// ============================================================================
// MOCK AUTH FUNCTIONS - Simulate network latency and JWT behavior
// ============================================================================

const simulateNetworkDelay = () => new Promise((resolve) => setTimeout(resolve, 500 + Math.random() * 500))

const generateMockToken = (userId: string): string => {
  // Simulate JWT token (in production, this comes from backend)
  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }))
  const payload = btoa(
    JSON.stringify({
      userId,
      exp: Date.now() + 3600000, // 1 hour expiry
    }),
  )
  const signature = btoa("mock-signature")
  return `${header}.${payload}.${signature}`
}

export const mockAuth = {
  /**
   * Mock login function
   * TO REPLACE: fetch(API_ENDPOINTS.login, {
   *   method: 'POST',
   *   headers: { 'Content-Type': 'application/json' },
   *   body: JSON.stringify({ email, password })
   * }).then(res => res.json())
   */
  login: async (email: string, password: string): Promise<AuthResponse> => {
    await simulateNetworkDelay()

    const user = MOCK_USERS.find((u) => u.email === email && u.password === password)

    if (!user) {
      return {
        success: false,
        message: "Invalid email or password",
      }
    }

    const token = generateMockToken(user.id)
    const { password: _, ...userWithoutPassword } = user

    return {
      success: true,
      token,
      user: userWithoutPassword,
    }
  },

  /**
   * Mock register function
   * TO REPLACE: fetch(API_ENDPOINTS.register, {
   *   method: 'POST',
   *   headers: { 'Content-Type': 'application/json' },
   *   body: JSON.stringify({ email, password, name })
   * }).then(res => res.json())
   */
  register: async (email: string, password: string, name: string): Promise<AuthResponse> => {
    await simulateNetworkDelay()

    // Check if user already exists
    const existingUser = MOCK_USERS.find((u) => u.email === email)
    if (existingUser) {
      return {
        success: false,
        message: "User with this email already exists",
      }
    }

    // Create new user
    const newUser: User = {
      id: String(MOCK_USERS.length + 1),
      email,
      password,
      name,
      createdAt: new Date().toISOString(),
    }

    MOCK_USERS.push(newUser)

    const token = generateMockToken(newUser.id)
    const { password: _, ...userWithoutPassword } = newUser

    return {
      success: true,
      token,
      user: userWithoutPassword,
    }
  },

  /**
   * Mock get profile function
   * TO REPLACE: fetch(API_ENDPOINTS.profile, {
   *   method: 'GET',
   *   headers: {
   *     'Authorization': `Bearer ${token}`,
   *     'Content-Type': 'application/json'
   *   }
   * }).then(res => res.json())
   */
  getProfile: async (token: string): Promise<ProfileResponse> => {
    await simulateNetworkDelay()

    try {
      // Decode mock token
      const payload = JSON.parse(atob(token.split(".")[1]))

      // Check if token is expired
      if (payload.exp < Date.now()) {
        return {
          success: false,
          message: "Token expired",
        }
      }

      const user = MOCK_USERS.find((u) => u.id === payload.userId)

      if (!user) {
        return {
          success: false,
          message: "User not found",
        }
      }

      const { password: _, ...userWithoutPassword } = user

      return {
        success: true,
        user: userWithoutPassword,
      }
    } catch (error) {
      return {
        success: false,
        message: "Invalid token",
      }
    }
  },

  /**
   * Mock logout function
   * TO REPLACE: fetch(API_ENDPOINTS.logout, {
   *   method: 'POST',
   *   headers: { 'Authorization': `Bearer ${token}` }
   * })
   */
  logout: async (): Promise<{ success: boolean }> => {
    await simulateNetworkDelay()
    return { success: true }
  },
}

// ============================================================================
// UI CONTENT - LogicGuard Landing Page
// ============================================================================

export const LANDING_CONTENT = {
  brand: {
    name: "LogicGuard",
    tagline: "Write with clarity, backed by logic",
  },
  hero: {
    title: "Your AI writing assistant for logical coherence",
    subtitle:
      "LogicGuard helps you write better by focusing on what matters: clear logic, strong arguments, and goal alignment—not just grammar.",
    cta: "Start writing for free",
  },
  features: [
    {
      title: "Context-aware feedback",
      description:
        "Set your writing goals and rubric criteria. LogicGuard checks your logic against what you're trying to achieve.",
      icon: "target",
    },
    {
      title: "Real-time logic checking",
      description:
        "Catch contradictions, undefined terms, and weak arguments as you write—before they become problems.",
      icon: "shield",
    },
    {
      title: "Goal alignment dashboard",
      description:
        "Track how well your writing meets your objectives with clear metrics on argument coherence and evidence quality.",
      icon: "chart",
    },
  ],
  writingTypes: ["Essay", "Proposal", "Report", "Pitch", "Blog Post", "Research Paper", "Business Case"],
}
