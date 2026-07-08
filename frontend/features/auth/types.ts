export interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  auth_provider: string;
  avatar_url: string | null;
  email_verified: boolean;
  verification_sent_at: string | null;
}

export interface VerificationResponse {
  message: string;
}

export interface ResendVerificationResponse {
  message: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  identifier: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
}

export interface PasswordResetResponse {
  message: string;
}

export interface DeleteAccountRequest {
  password: string;
}

export interface GoogleCallbackRequest {
  code: string;
}
