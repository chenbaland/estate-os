export type RoleCode =
  | "super_admin"
  | "estate_admin"
  | "facility_admin"
  | "security_admin"
  | "finance_admin"
  | "resident"
  | "vendor"
  | "technician"
  | "security_personnel";

export interface User {
  id: string;
  email: string;
  username: string;
  phone: string;
  first_name: string;
  last_name: string;
  avatar: string | null;
  mfa_enabled: boolean;
  preferred_language: string;
  timezone: string;
}

export interface UserRole {
  id: string;
  code: RoleCode;
  name: string;
  estate_id: string;
  estate_name: string;
}

export interface Estate {
  id: string;
  name: string;
  slug: string;
  address: string;
  city: string;
  country: string;
  logo: string | null;
  timezone: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface VisitorPass {
  id: string;
  visitor_name: string;
  visitor_phone: string;
  purpose: string;
  valid_from: string;
  valid_until: string;
  qr_code: string;
  status: "active" | "expired" | "used" | "revoked";
}

export interface MaintenanceRequest {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: "low" | "medium" | "high" | "urgent";
  status: "open" | "in_progress" | "resolved" | "closed";
  created_at: string;
}

export interface BillingInvoice {
  id: string;
  title: string;
  amount: number;
  currency: string;
  due_date: string;
  status: "pending" | "paid" | "overdue";
}

export interface Facility {
  id: string;
  name: string;
  description: string;
  capacity: number;
  hourly_rate: number;
  image_url: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ApiListResponse<T> {
  data: T[];
  pagination?: {
    cursor: string | null;
    has_more: boolean;
    count: number;
  };
}

export interface ApiError {
  detail?: string;
  title?: string;
  message?: string;
  errors?: Array<{ field: string; message: string }>;
}
