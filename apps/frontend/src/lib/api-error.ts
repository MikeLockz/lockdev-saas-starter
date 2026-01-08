import { AxiosError } from "axios";

/**
 * Standard API error response shape from the backend.
 */
export interface ApiErrorResponse {
  detail: string | ValidationErrorDetail[];
}

export interface ValidationErrorDetail {
  loc: (string | number)[];
  msg: string;
  type: string;
}

/**
 * Extract a user-friendly error message from an unknown error.
 * Handles Axios errors with API responses, standard Errors, and unknown types.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as ApiErrorResponse | undefined;

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail) && data.detail.length > 0) {
      return data.detail[0]?.msg || "Validation error";
    }

    // Fallback to HTTP status text or generic message
    return error.response?.statusText || error.message || "Request failed";
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unknown error occurred";
}

/**
 * Type guard to check if an error is an AxiosError with a specific status code.
 */
export function isAxiosError(error: unknown): error is AxiosError {
  return error instanceof AxiosError;
}

/**
 * Check if error indicates a 401 Unauthorized response.
 */
export function isUnauthorizedError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 401;
}

/**
 * Check if error indicates a 403 Forbidden response.
 */
export function isForbiddenError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 403;
}

/**
 * Check if error indicates a 404 Not Found response.
 */
export function isNotFoundError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 404;
}

/**
 * Check if error indicates a 409 Conflict response.
 */
export function isConflictError(error: unknown): boolean {
  return isAxiosError(error) && error.response?.status === 409;
}
