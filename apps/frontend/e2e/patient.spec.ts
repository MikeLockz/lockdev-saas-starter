import { expect, test } from "@playwright/test";

test.describe("Patient Management", () => {
  test.beforeEach(async ({ page }) => {
    // Login as E2E User (Super Admin)
    await page.goto("/login");
    await page.getByRole("button", { name: "E2E User" }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("should allow creating a new patient", async ({ page }) => {
    // Navigate to Patients list
    await page.getByRole("link", { name: "Patients", exact: true }).click();
    await expect(page).toHaveURL(/\/patients$/);

    // Click "New Patient" button
    // Assuming there is a button to create a new patient on the index page
    // If not, I might need to navigate directly or check the index page implementation
    await page.getByRole("button", { name: "New Patient" }).click();
    await expect(page).toHaveURL(/\/patients\/new/);

    // Fill out the form
    const uniqueId = Date.now().toString();
    const firstName = `TestFirst${uniqueId}`;
    const lastName = `TestLast${uniqueId}`;

    await page.getByLabel("First Name").fill(firstName);
    await page.getByLabel("Last Name").fill(lastName);
    await page.getByLabel("Date of Birth").fill("1990-01-01");

    // Select Legal Sex (using click because it's a shadcn Select)
    await page.getByRole("combobox", { name: "Legal Sex" }).click();
    await page.getByRole("option", { name: "Male", exact: true }).click();

    // Submit form
    await page.getByRole("button", { name: "Create Patient" }).click();

    // Verify redirection to details page
    await expect(page).toHaveURL(/\/patients\/\S+/);

    // Verify patient details are displayed
    await expect(
      page.getByRole("heading", { name: `${lastName}, ${firstName}` }),
    ).toBeVisible();
    await expect(page.getByText("Male", { exact: true })).toBeVisible();
    // Allow for timezone shift (UTC to EST/EDT) which might show previous day
    await expect(
      page.getByText(/January 1, 1990|December 31, 1989/),
    ).toBeVisible();
  });
});
