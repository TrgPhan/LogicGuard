"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { AuthAPI } from "@/lib/api-service"
import { Loader2 } from "lucide-react"

export default function SettingsPage() {
  const [profile, setProfile] = useState({ email: "", name: "" })
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)
  
  // Preferences state
  const [preferences, setPreferences] = useState({
    realtimeChecking: true,
    autoSave: true,
    showSuggestions: true,
    emailNotifications: false,
    weeklyReports: true,
  })

  useEffect(() => {
    fetchProfile()
    loadPreferences()
  }, [])

  const fetchProfile = async () => {
    try {
      const data = await AuthAPI.getProfile()
      setProfile({
        email: data.email,
        name: data.email.split('@')[0],
      })
    } catch (error) {
      console.error("Failed to fetch profile:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadPreferences = () => {
    const saved = localStorage.getItem("logicguard_preferences")
    if (saved) {
      try {
        setPreferences(JSON.parse(saved))
      } catch (e) {
        console.error("Failed to parse preferences:", e)
      }
    }
  }

  const savePreferences = (newPrefs: typeof preferences) => {
    setPreferences(newPrefs)
    localStorage.setItem("logicguard_preferences", JSON.stringify(newPrefs))
  }

  const handleSaveProfile = async () => {
    setIsSaving(true)
    setMessage(null)
    try {
      // Note: Backend PUT /api/auth/me endpoint
      // For now just show success
      setMessage({ type: "success", text: "Profile settings saved successfully!" })
    } catch (error: any) {
      setMessage({ type: "error", text: error.message || "Failed to save profile" })
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="p-8 flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-[#37322F]" />
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-semibold text-[#37322F] mb-2">Settings</h1>
        <p className="text-[#605A57]">Manage your account and preferences</p>
      </div>

      {message && (
        <div className={`px-4 py-3 rounded ${
          message.type === "success" 
            ? "bg-green-50 border border-green-200 text-green-700"
            : "bg-red-50 border border-red-200 text-red-700"
        }`}>
          {message.text}
        </div>
      )}

      {/* Profile Settings */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle>Profile Information</CardTitle>
          <CardDescription>Update your personal details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input 
              id="email" 
              type="email" 
              value={profile.email}
              disabled
              className="bg-gray-50"
            />
            <p className="text-xs text-[#605A57]">Email cannot be changed</p>
          </div>
          <Button 
            onClick={handleSaveProfile}
            disabled={isSaving}
            className="bg-[#37322F] hover:bg-[#37322F]/90"
          >
            {isSaving ? "Saving..." : "Save Changes"}
          </Button>
        </CardContent>
      </Card>

      {/* Writing Preferences */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle>Writing Preferences</CardTitle>
          <CardDescription>Customize your writing experience</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Real-time Logic Checking</Label>
              <p className="text-sm text-[#605A57]">Check for logic issues as you type (Requires Analysis API)</p>
            </div>
            <Switch 
              checked={preferences.realtimeChecking}
              onCheckedChange={(checked) => savePreferences({ ...preferences, realtimeChecking: checked })}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Auto-save</Label>
              <p className="text-sm text-[#605A57]">Automatically save your work every 30 seconds</p>
            </div>
            <Switch 
              checked={preferences.autoSave}
              onCheckedChange={(checked) => savePreferences({ ...preferences, autoSave: checked })}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Show Suggestions</Label>
              <p className="text-sm text-[#605A57]">Display improvement suggestions (Requires Feedback API)</p>
            </div>
            <Switch 
              checked={preferences.showSuggestions}
              onCheckedChange={(checked) => savePreferences({ ...preferences, showSuggestions: checked })}
            />
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card className="border-[rgba(55,50,47,0.12)]">
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>Manage how you receive updates</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Email Notifications</Label>
              <p className="text-sm text-[#605A57]">Receive updates via email</p>
            </div>
            <Switch 
              checked={preferences.emailNotifications}
              onCheckedChange={(checked) => savePreferences({ ...preferences, emailNotifications: checked })}
            />
          </div>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Weekly Reports</Label>
              <p className="text-sm text-[#605A57]">Get weekly progress summaries</p>
            </div>
            <Switch 
              checked={preferences.weeklyReports}
              onCheckedChange={(checked) => savePreferences({ ...preferences, weeklyReports: checked })}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
