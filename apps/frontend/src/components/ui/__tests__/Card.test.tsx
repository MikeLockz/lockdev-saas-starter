import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../card";

describe("Card", () => {
  it("renders complete card structure", () => {
    const { asFragment } = render(
      <Card>
        <CardHeader>
          <CardTitle>Card Title</CardTitle>
          <CardDescription>Card Description</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Card content goes here</p>
        </CardContent>
        <CardFooter>
          <p>Card footer</p>
        </CardFooter>
      </Card>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders card with header only", () => {
    const { asFragment } = render(
      <Card>
        <CardHeader>
          <CardTitle>Simple Card</CardTitle>
        </CardHeader>
      </Card>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders card with content only", () => {
    const { asFragment } = render(
      <Card>
        <CardContent>Content without header</CardContent>
      </Card>,
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
