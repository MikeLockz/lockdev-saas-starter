import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Button } from "../button";

describe("Button", () => {
  describe("variants", () => {
    it("renders default variant", () => {
      const { asFragment } = render(<Button>Click me</Button>);
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders destructive variant", () => {
      const { asFragment } = render(
        <Button variant="destructive">Delete</Button>,
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders outline variant", () => {
      const { asFragment } = render(<Button variant="outline">Outline</Button>);
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders secondary variant", () => {
      const { asFragment } = render(
        <Button variant="secondary">Secondary</Button>,
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders ghost variant", () => {
      const { asFragment } = render(<Button variant="ghost">Ghost</Button>);
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders link variant", () => {
      const { asFragment } = render(<Button variant="link">Link</Button>);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("sizes", () => {
    it("renders default size", () => {
      const { asFragment } = render(<Button size="default">Default</Button>);
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders sm size", () => {
      const { asFragment } = render(<Button size="sm">Small</Button>);
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders lg size", () => {
      const { asFragment } = render(<Button size="lg">Large</Button>);
      expect(asFragment()).toMatchSnapshot();
    });

    it("renders icon size", () => {
      const { asFragment } = render(<Button size="icon">🔔</Button>);
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("states", () => {
    it("renders disabled state", () => {
      const { asFragment } = render(<Button disabled>Disabled</Button>);
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
