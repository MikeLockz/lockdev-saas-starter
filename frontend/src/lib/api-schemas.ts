import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const ImpersonationRequest = z.object({ reason: z.string() }).passthrough();
const ValidationError = z
  .object({
    loc: z.array(z.union([z.string(), z.number()])),
    msg: z.string(),
    type: z.string(),
  })
  .passthrough();
const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough();
const ConsentSignRequest = z.object({ document_id: z.string() }).passthrough();
const UserRead = z
  .object({
    id: z.string().uuid(),
    email: z.string().email(),
    is_active: z.boolean(),
    is_super_admin: z.boolean(),
    full_name: z.union([z.string(), z.null()]).optional(),
    role: z.string().optional().default("guest"),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.string().datetime({ offset: true }),
  })
  .passthrough();

export const schemas = {
  ImpersonationRequest,
  ValidationError,
  HTTPValidationError,
  ConsentSignRequest,
  UserRead,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/api/v1/admin/impersonate/:patient_id",
    alias: "impersonate_patient_api_v1_admin_impersonate__patient_id__post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ reason: z.string() }).passthrough(),
      },
      {
        name: "patient_id",
        type: "Path",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/consent",
    alias: "sign_consent_api_v1_consent_post",
    description: `Sign a specific consent document.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({ document_id: z.string() }).passthrough(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/consent/required",
    alias: "get_required_consents_api_v1_consent_required_get",
    description: `List all active consents and status for the current user.`,
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/api/v1/me",
    alias: "read_users_me_api_v1_me_get",
    description: `Get current user.`,
    requestFormat: "json",
    response: UserRead,
  },
  {
    method: "get",
    path: "/health",
    alias: "health_check_health_get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "get",
    path: "/health/deep",
    alias: "deep_health_check_health_deep_get",
    requestFormat: "json",
    response: z.unknown(),
  },
]);

export const api = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
