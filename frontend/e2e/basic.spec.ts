import { expect, test } from "@playwright/test";

test("has title", async ({ page }) => {
  await page.goto("/");
  // By default Vite + React template has title "Vite + React" or similar
  await expect(page).toHaveTitle(/Vite/);
});
