import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/lib/api/query-keys";
import {
  loginUser,
  registerUser,
  logoutUser,
  forgotPassword,
  resetPassword,
  deleteAccount,
} from "@/features/auth/api";
import type {
  LoginRequest,
  RegisterRequest,
  RegisterResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  DeleteAccountRequest,
} from "@/features/auth/types";

export function useLoginMutation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: LoginRequest) => loginUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me });
      router.push("/dashboard");
    },
  });
}

export function useRegisterMutation() {
  const router = useRouter();

  return useMutation({
    mutationFn: (data: RegisterRequest) => registerUser(data),
    onSuccess: (data: RegisterResponse) => {
      router.push(`/auth/verify-email-prompt?email_sent=${data.email_sent}`);
    },
  });
}

export function useForgotPasswordMutation() {
  return useMutation({
    mutationFn: (data: ForgotPasswordRequest) => forgotPassword(data),
  });
}

export function useResetPasswordMutation() {
  const router = useRouter();

  return useMutation({
    mutationFn: (data: ResetPasswordRequest) => resetPassword(data),
    onSuccess: () => {
      setTimeout(() => router.push("/login"), 3000);
    },
  });
}

export function useDeleteAccountMutation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: DeleteAccountRequest) => deleteAccount(data),
    onSuccess: () => {
      queryClient.setQueryData(queryKeys.auth.me, null);
      router.push("/login");
    },
  });
}

export function useLogoutMutation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () => logoutUser(),
    onSuccess: () => {
      queryClient.setQueryData(queryKeys.auth.me, null);
      router.push("/login");
    },
  });
}
