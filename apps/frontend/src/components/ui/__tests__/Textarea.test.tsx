import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Textarea } from "../textarea";

describe("Textarea", () => {
  it("renders default state", () => {
    const { asFragment } = render(<Textarea />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders with placeholder", () => {
    const { asFragment } = render(
      <Textarea placeholder="Enter your message..." />,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders disabled state", () => {
    const { asFragment } = render(<Textarea disabled />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders with rows attribute", () => {
    const { asFragment } = render(<Textarea rows={5} />);
    expect(asFragment()).toMatchSnapshot();
  });
});
