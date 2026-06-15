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
  is_superuser?: boolean;
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
  estate_id: string;
  unit_id: string;
}

export type ResidentType = "owner" | "tenant";

export type MembershipStatus = "pending" | "active" | "inactive" | "suspended";

export interface ResidentMembership {
  resident_profile_id: string;
  estate_id: string;
  estate_name: string;
  estate_slug: string;
  resident_type: ResidentType | null;
  resident_type_label: string;
  status: MembershipStatus;
  unit_id: string | null;
  unit_number: string | null;
}

export interface PublicEstate {
  id: string;
  name: string;
  slug: string;
  city: string;
  state: string;
  country: string;
}

export interface PublicUnit {
  id: string;
  unit_number: string;
  unit_type: string;
  floor: number;
  bedrooms: number;
  bathrooms: number;
}

export interface CurrentUserResponse {
  user: User;
  memberships: ResidentMembership[];
  roles: UserRole[];
  has_active_membership: boolean;
  pending_membership: boolean;
}

export interface AuthSessionResponse extends AuthTokens {
  user?: User;
  memberships?: ResidentMembership[];
  roles?: UserRole[];
  has_active_membership?: boolean;
  pending_membership?: boolean;
}

export interface ResidentProfile {
  id: string;
  estate: string;
  user: string;
  user_email?: string;
  user_first_name?: string;
  user_last_name?: string;
  unit: string | null;
  unit_number?: string;
  resident_type: ResidentType | null;
  status: MembershipStatus;
  is_primary: boolean;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface Unit {
  id: string;
  estate: string;
  unit_number: string;
  occupancy_status: string;
  is_active: boolean;
}

export interface PlatformOverview {
  estates_total: number;
  estates_active: number;
  users_total: number;
  estate_admins_total: number;
  pending_registrations: number;
  units_total: number;
}

export interface PlatformEstate {
  id: string;
  name: string;
  slug: string;
  estate_type: string;
  tier: string;
  description: string;
  city: string;
  state: string;
  country: string;
  address_line1: string;
  contact_email: string;
  contact_phone: string;
  timezone: string;
  currency: string;
  total_units: number;
  occupied_units: number;
  is_active: boolean;
  admin_count: number;
  pending_residents: number;
  created_at: string;
}

export interface PlatformAdminAssignment {
  id: string;
  user_id: string;
  user_email: string;
  user_first_name: string;
  user_last_name: string;
  estate_id: string;
  estate_name: string;
  role_code: RoleCode;
  role_name: string;
  is_active: boolean;
  created_at: string;
}

export interface CreatePlatformEstatePayload {
  name: string;
  slug?: string;
  estate_type?: string;
  tier?: string;
  description?: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  country?: string;
  contact_email?: string;
  contact_phone?: string;
  timezone?: string;
  currency?: string;
  total_units?: number;
  is_active?: boolean;
}

export type UpdatePlatformEstatePayload = Omit<CreatePlatformEstatePayload, "slug">;

export interface PlatformAuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  actor_id: string | null;
  actor_email: string | null;
  actor_name: string | null;
  estate_id: string | null;
  estate_name: string | null;
  summary: string;
  metadata: Record<string, unknown>;
  ip_address: string | null;
  trace_id: string;
  created_at: string;
}

export interface AssignPlatformAdminPayload {
  email: string;
  first_name?: string;
  last_name?: string;
  estate_id: string;
  role_code: "estate_admin" | "finance_admin" | "security_admin" | "facility_admin";
}

export interface PaginatedResponse<T> {
  results: T[];
  next: string | null;
  previous: string | null;
}

export type InvoiceStatus =
  | "draft"
  | "issued"
  | "partial"
  | "paid"
  | "overdue"
  | "cancelled"
  | "written_off";

export interface Invoice {
  id: string;
  estate: string;
  invoice_number: string;
  unit: string;
  resident: string | null;
  status: InvoiceStatus;
  issue_date: string;
  due_date: string;
  subtotal: string;
  tax_amount: string;
  discount_amount: string;
  total_amount: string;
  amount_paid: string;
  balance_due: string;
  currency: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export type PaymentStatus = "pending" | "processing" | "completed" | "failed" | "refunded";

export interface Payment {
  id: string;
  estate: string;
  invoice: string;
  payer: string | null;
  reference: string;
  method: string;
  status: PaymentStatus;
  amount: string;
  currency: string;
  paid_at: string | null;
  created_at: string;
}

export type DebtStatus =
  | "current"
  | "overdue"
  | "in_collection"
  | "settled"
  | "written_off";

export interface DebtRecord {
  id: string;
  estate: string;
  unit: string;
  resident: string | null;
  total_debt: string;
  overdue_amount: string;
  oldest_due_date: string | null;
  status: DebtStatus;
  last_payment_date: string | null;
  notes: string;
  created_at: string;
}

export type VisitorPassStatus = "active" | "used" | "expired" | "revoked";
export type VisitorPassType = "single" | "multi" | "recurring";

export interface VisitorPass {
  id: string;
  estate: string;
  host: string;
  visitor_name: string;
  visitor_phone: string;
  visitor_email: string;
  pass_type: VisitorPassType;
  status: VisitorPassStatus;
  qr_code: string;
  valid_from: string;
  valid_until: string;
  max_entries: number;
  entries_used: number;
  vehicle_plate: string;
  purpose: string;
  created_at: string;
}

export interface CreateVisitorPassPayload {
  host: string;
  visitor_name: string;
  visitor_phone?: string;
  purpose?: string;
  pass_type?: VisitorPassType;
  valid_until: string;
  max_entries?: number;
}

export type VisitorLogDirection = "entry" | "exit";

export interface VisitorLog {
  id: string;
  estate: string;
  visitor_pass: string | null;
  visitor_name: string;
  visitor_phone: string;
  host: string | null;
  direction: VisitorLogDirection;
  verification_method: string;
  gate_name: string;
  timestamp: string;
  created_at: string;
}

export interface BlacklistEntry {
  id: string;
  estate: string;
  full_name: string;
  phone: string;
  email: string;
  reason: string;
  description: string;
  is_active: boolean;
  created_at: string;
}

export interface ApiError {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

export interface NavItem {
  title: string;
  href: string;
  icon: string;
  roles?: RoleCode[];
}

export interface DashboardStat {
  label: string;
  value: string | number;
  change?: number;
  trend?: "up" | "down" | "neutral";
}

export type NotificationStatus = "pending" | "sent" | "delivered" | "read" | "failed";
export type NotificationPriority = "low" | "normal" | "high" | "critical";
export type NotificationChannel = "email" | "sms" | "whatsapp" | "push" | "inapp";

export interface Notification {
  id: string;
  estate: string;
  recipient: string;
  template: string | null;
  channel: NotificationChannel;
  status: NotificationStatus;
  priority: NotificationPriority;
  title: string;
  body: string;
  data: Record<string, unknown>;
  action_url: string | null;
  sent_at: string | null;
  delivered_at: string | null;
  read_at: string | null;
  error_message: string;
  external_id: string;
  created_at: string;
  updated_at: string;
}
