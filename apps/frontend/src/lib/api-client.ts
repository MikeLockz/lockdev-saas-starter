import { createApiClient } from "./api-schemas";
import { api as axiosInstance } from "./axios";

const baseURL = axiosInstance.defaults.baseURL || "http://localhost:8000";

export const api = createApiClient(baseURL, {
  axiosInstance,
});

export * from "./api-schemas";
