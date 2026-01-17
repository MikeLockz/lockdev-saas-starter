import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock import.meta.env
vi.stubEnv("VITE_FIREBASE_API_KEY", "mock-api-key");
vi.stubEnv("VITE_FIREBASE_AUTH_DOMAIN", "mock-auth-domain");
vi.stubEnv("VITE_FIREBASE_PROJECT_ID", "mock-project-id");
vi.stubEnv("VITE_FIREBASE_STORAGE_BUCKET", "mock-storage-bucket");
vi.stubEnv("VITE_FIREBASE_MESSAGING_SENDER_ID", "mock-messaging-sender-id");
vi.stubEnv("VITE_FIREBASE_APP_ID", "mock-app-id");

// Mock Firebase
vi.mock("firebase/app", () => ({
  initializeApp: vi.fn(() => ({})),
}));

vi.mock("firebase/auth", () => ({
  getAuth: vi.fn(() => ({
    currentUser: null,
    onAuthStateChanged: vi.fn(),
  })),
}));
