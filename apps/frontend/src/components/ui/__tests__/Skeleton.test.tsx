import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Skeleton } from "../skeleton";

describe("Skeleton", () => {
  it("renders default shape", () => {
    const { asFragment } = render(<Skeleton className="h-4 w-[250px]" />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders circle shape", () => {
    const { asFragment } = render(
      <Skeleton className="h-12 w-12 rounded-full" />,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders card skeleton", () => {
    const { asFragment } = render(
      <div className="flex flex-col space-y-3">
        <Skeleton className="h-[125px] w-[250px] rounded-xl" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-[250px]" />
          <Skeleton className="h-4 w-[200px]" />
        </div>
      </div>,
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
