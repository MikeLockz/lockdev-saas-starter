import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Input } from "../input";

describe("Input", () => {
  it("renders default state", () => {
    const { asFragment } = render(<Input />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders with placeholder", () => {
    const { asFragment } = render(<Input placeholder="Enter your name" />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders disabled state", () => {
    const { asFragment } = render(<Input disabled />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders file type", () => {
    const { asFragment } = render(<Input type="file" />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders password type", () => {
    const { asFragment } = render(<Input type="password" />);
    expect(asFragment()).toMatchSnapshot();
  });
});
