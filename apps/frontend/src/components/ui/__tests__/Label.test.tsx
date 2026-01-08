import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Label } from "../label";

describe("Label", () => {
  it("renders default text style", () => {
    const { asFragment } = render(<Label>Email Address</Label>);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders with htmlFor attribute", () => {
    const { asFragment } = render(<Label htmlFor="email">Email</Label>);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders with custom className", () => {
    const { asFragment } = render(
      <Label className="text-red-500">Required Field</Label>,
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
