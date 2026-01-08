import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Progress } from "../progress";

describe("Progress", () => {
  it("renders 0% value", () => {
    const { asFragment } = render(<Progress value={0} />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders 50% value", () => {
    const { asFragment } = render(<Progress value={50} />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders 100% value", () => {
    const { asFragment } = render(<Progress value={100} />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders without value (undefined)", () => {
    const { asFragment } = render(<Progress />);
    expect(asFragment()).toMatchSnapshot();
  });
});
