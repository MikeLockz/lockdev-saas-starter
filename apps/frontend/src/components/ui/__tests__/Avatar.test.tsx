import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Avatar, AvatarFallback, AvatarImage } from "../avatar";

describe("Avatar", () => {
  it("renders with image", () => {
    const { asFragment } = render(
      <Avatar>
        <AvatarImage src="https://example.com/avatar.jpg" alt="User" />
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders fallback state", () => {
    const { asFragment } = render(
      <Avatar>
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders with custom className", () => {
    const { asFragment } = render(
      <Avatar className="h-16 w-16">
        <AvatarFallback>AB</AvatarFallback>
      </Avatar>,
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
