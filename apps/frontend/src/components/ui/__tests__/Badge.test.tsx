import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "../badge";

describe("Badge", () => {
  it("renders default variant", () => {
    const { asFragment } = render(<Badge>Default</Badge>);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders secondary variant", () => {
    const { asFragment } = render(<Badge variant="secondary">Secondary</Badge>);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders destructive variant", () => {
    const { asFragment } = render(
      <Badge variant="destructive">Destructive</Badge>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders outline variant", () => {
    const { asFragment } = render(<Badge variant="outline">Outline</Badge>);
    expect(asFragment()).toMatchSnapshot();
  });
});
