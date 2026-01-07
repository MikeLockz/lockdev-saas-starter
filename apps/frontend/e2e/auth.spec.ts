import { expect, test } from "@playwright/test";

test("allows dev login as E2E user", async ({ page }) => {
  await page.goto("/login");

  // Click the Dev Login button
  await page.getByRole("button", { name: "E2E User" }).click();

  // Wait for navigation to dashboard
  await expect(page).toHaveURL(/\/dashboard/);

  // Verify welcome message
  await expect(page.getByText("Welcome, e2e@example.com!")).toBeVisible();
});
