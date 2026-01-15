import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Switch } from "../switch";

describe("Switch", () => {
  it("renders unchecked state", () => {
    const { asFragment } = render(<Switch />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders checked state", () => {
    const { asFragment } = render(<Switch checked />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders disabled state", () => {
    const { asFragment } = render(<Switch disabled />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders disabled and checked state", () => {
    const { asFragment } = render(<Switch disabled checked />);
    expect(asFragment()).toMatchSnapshot();
  });
});
