"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { authUtils, validation } from "@/lib/auth"
import Link from "next/link"

interface AuthFormProps {
  mode: "login" | "register"
}

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: "error" | "success"; text: string } | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    const emailValidation = validation.email(formData.email)
    if (!emailValidation.valid) {
      newErrors.email = emailValidation.message || ""
    }

    const passwordValidation = validation.password(formData.password)
    if (!passwordValidation.valid) {
      newErrors.password = passwordValidation.message || ""
    }

    if (mode === "register") {
      const nameValidation = validation.name(formData.name)
      if (!nameValidation.valid) {
        newErrors.name = nameValidation.message || ""
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      let response
      if (mode === "login") {
        response = await authUtils.login(formData.email, formData.password)
      } else {
        response = await authUtils.register(formData.email, formData.password, formData.name)
      }

      if (response.success) {
        setMessage({ type: "success", text: `${mode === "login" ? "Login" : "Registration"} successful!` })
        setTimeout(() => {
          router.push("/profile")
        }, 500)
      } else {
        setMessage({ type: "error", text: response.message || "An error occurred" })
      }
    } catch (error) {
      setMessage({ type: "error", text: "An unexpected error occurred" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white shadow-lg rounded-lg p-8 border border-[rgba(55,50,47,0.12)]">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-[#37322F] mb-2">
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h2>
          <p className="text-[#605A57] text-sm">
            {mode === "login" ? "Sign in to continue to LogicGuard" : "Start writing with clarity and confidence"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <div>
              <Label htmlFor="name" className="text-[#37322F]">
                Name
              </Label>
              <Input
                id="name"
                name="name"
                type="text"
                value={formData.name}
                onChange={handleChange}
                className={`mt-1 ${errors.name ? "border-red-500" : ""}`}
                placeholder="John Doe"
              />
              {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
            </div>
          )}

          <div>
            <Label htmlFor="email" className="text-[#37322F]">
              Email
            </Label>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={`mt-1 ${errors.email ? "border-red-500" : ""}`}
              placeholder="you@example.com"
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
          </div>

          <div>
            <Label htmlFor="password" className="text-[#37322F]">
              Password
            </Label>
            <Input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className={`mt-1 ${errors.password ? "border-red-500" : ""}`}
              placeholder="••••••••"
            />
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
          </div>

          {message && (
            <div
              className={`p-3 rounded-md text-sm ${
                message.type === "error"
                  ? "bg-red-50 text-red-700 border border-red-200"
                  : "bg-green-50 text-green-700 border border-green-200"
              }`}
            >
              {message.text}
            </div>
          )}

          <Button type="submit" disabled={loading} className="w-full bg-[#37322F] hover:bg-[#37322F]/90 text-white">
            {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-[#605A57]">
          {mode === "login" ? (
            <>
              Don't have an account?{" "}
              <Link href="/register" className="text-[#37322F] font-medium hover:underline">
                Sign up
              </Link>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <Link href="/login" className="text-[#37322F] font-medium hover:underline">
                Sign in
              </Link>
            </>
          )}
        </div>

        {mode === "login" && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-xs text-blue-700 font-medium mb-1">Demo credentials:</p>
            <p className="text-xs text-blue-600">Email: demo@logicguard.com</p>
            <p className="text-xs text-blue-600">Password: password123</p>
          </div>
        )}
      </div>
    </div>
  )
}
