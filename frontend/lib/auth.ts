"use client"

import { mockAuth } from "./constants"

// ============================================================================
// CLIENT-SIDE AUTH UTILITIES
// ============================================================================

const TOKEN_KEY = "logicguard_token"
const USER_KEY = "logicguard_user"

export const authUtils = {
  // Store token in localStorage
  setToken: (token: string) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, token)
    }
  },

  // Get token from localStorage
  getToken: (): string | null => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(TOKEN_KEY)
    }
    return null
  },

  // Remove token from localStorage
  removeToken: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    }
  },

  // Store user data
  setUser: (user: any) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    }
  },

  // Get user data
  getUser: () => {
    if (typeof window !== "undefined") {
      const user = localStorage.getItem(USER_KEY)
      return user ? JSON.parse(user) : null
    }
    return null
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return !!authUtils.getToken()
  },

  // Login
  login: async (email: string, password: string) => {
    const response = await mockAuth.login(email, password)

    if (response.success && response.token && response.user) {
      authUtils.setToken(response.token)
      authUtils.setUser(response.user)
    }

    return response
  },

  // Register
  register: async (email: string, password: string, name: string) => {
    const response = await mockAuth.register(email, password, name)

    if (response.success && response.token && response.user) {
      authUtils.setToken(response.token)
      authUtils.setUser(response.user)
    }

    return response
  },

  // Logout
  logout: async () => {
    await mockAuth.logout()
    authUtils.removeToken()
  },

  // Get profile
  getProfile: async () => {
    const token = authUtils.getToken()
    if (!token) {
      return { success: false, message: "No token found" }
    }

    return await mockAuth.getProfile(token)
  },
}

// ============================================================================
// VALIDATION UTILITIES
// ============================================================================

export const validation = {
  email: (email: string): { valid: boolean; message?: string } => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email) {
      return { valid: false, message: "Email is required" }
    }
    if (!emailRegex.test(email)) {
      return { valid: false, message: "Invalid email format" }
    }
    return { valid: true }
  },

  password: (password: string): { valid: boolean; message?: string } => {
    if (!password) {
      return { valid: false, message: "Password is required" }
    }
    if (password.length < 6) {
      return { valid: false, message: "Password must be at least 6 characters" }
    }
    return { valid: true }
  },

  name: (name: string): { valid: boolean; message?: string } => {
    if (!name) {
      return { valid: false, message: "Name is required" }
    }
    if (name.length < 2) {
      return { valid: false, message: "Name must be at least 2 characters" }
    }
    return { valid: true }
  },
}
