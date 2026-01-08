import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Button } from "../button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../tooltip";

describe("Tooltip", () => {
  it("renders tooltip with trigger", () => {
    const { asFragment } = render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline">Hover me</Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Tooltip content</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders tooltip with custom delay", () => {
    const { asFragment } = render(
      <TooltipProvider delayDuration={500}>
        <Tooltip>
          <TooltipTrigger>Delayed trigger</TooltipTrigger>
          <TooltipContent>Delayed tooltip</TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders tooltip with side offset", () => {
    const { asFragment } = render(
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger>Trigger</TooltipTrigger>
          <TooltipContent sideOffset={10}>Offset tooltip</TooltipContent>
        </Tooltip>
      </TooltipProvider>,
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
