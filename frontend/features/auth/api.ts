import { clientFetch, ApiError } from "@/lib/api/client";
import { API_ROUTES } from "@/lib/api/routes";
import type {
  User,
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  PasswordResetResponse,
  DeleteAccountRequest,
  VerificationResponse,
  ResendVerificationResponse,
} from "@/features/auth/types";

export async function loginUser(data: LoginRequest): Promise<User> {
  const result = await clientFetch<User>(API_ROUTES.AUTH.LOGIN, {
    method: "POST",
    body: JSON.stringify(data),
  });
  return result;
}

export async function registerUser(data: RegisterRequest): Promise<User> {
  const result = await clientFetch<User>(API_ROUTES.AUTH.REGISTER, {
    method: "POST",
    body: JSON.stringify(data),
  });
  return result;
}

export async function fetchCurrentUser(): Promise<User> {
  return clientFetch<User>(API_ROUTES.AUTH.ME);
}

export async function logoutUser(): Promise<void> {
  await clientFetch<void>(API_ROUTES.AUTH.LOGOUT, {
    method: "POST",
    body: JSON.stringify({ refresh_token: "" }),
  });
}

export async function forgotPassword(data: ForgotPasswordRequest): Promise<PasswordResetResponse> {
  return clientFetch<PasswordResetResponse>(API_ROUTES.AUTH.FORGOT_PASSWORD, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function resetPassword(data: ResetPasswordRequest): Promise<PasswordResetResponse> {
  return clientFetch<PasswordResetResponse>(API_ROUTES.AUTH.RESET_PASSWORD, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteAccount(data: DeleteAccountRequest): Promise<void> {
  await clientFetch<void>(API_ROUTES.AUTH.DELETE_ACCOUNT, {
    method: "DELETE",
    body: JSON.stringify(data),
  });
}

export async function verifyEmail(token: string): Promise<VerificationResponse> {
  return clientFetch<VerificationResponse>(`${API_ROUTES.AUTH.VERIFY_EMAIL}?token=${encodeURIComponent(token)}`);
}

export async function resendVerification(): Promise<ResendVerificationResponse> {
  return clientFetch<ResendVerificationResponse>(API_ROUTES.AUTH.RESEND_VERIFICATION, {
    method: "POST",
  });
}

export { ApiError };
