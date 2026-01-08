import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Separator } from "../separator";

describe("Separator", () => {
  it("renders horizontal orientation (default)", () => {
    const { asFragment } = render(<Separator />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders vertical orientation", () => {
    const { asFragment } = render(<Separator orientation="vertical" />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders with custom className", () => {
    const { asFragment } = render(<Separator className="my-4" />);
    expect(asFragment()).toMatchSnapshot();
  });
});
