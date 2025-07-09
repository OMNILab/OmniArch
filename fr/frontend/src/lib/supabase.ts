/// <reference types="vite/client" />
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types based on the data model
export interface User {
  id: string
  username: string
  role: 'organizer' | 'participant' | 'admin'
  department: string
  created_at: string
  updated_at: string
}

export interface MeetingRoom {
  id: string
  name: string
  location: string
  capacity: number
  equipment: string[]
  status: 'available' | 'booked'
  created_at: string
  updated_at: string
}

export interface Meeting {
  id: string
  room_id: string
  organizer_id: string
  title: string
  start_time: string
  duration_min: number
  status: 'booked' | 'cancelled'
  created_at: string
  updated_at: string
}

export interface MeetingTranscript {
  id: string
  meeting_id: string
  speaker_label: string
  content: string
  timestamp: string
  created_at: string
}

export interface MeetingMinutes {
  id: string
  meeting_id: string
  template_id: string
  summary: string
  points: string[]
  decisions: string[]
  raw_transcript: string
  editable_html: string
  created_at: string
}

export interface Task {
  id: string
  meeting_id: string
  description: string
  owner_id: string | null
  department: string
  due_date: string
  status: 'draft' | 'confirmed' | 'done'
  created_at: string
}