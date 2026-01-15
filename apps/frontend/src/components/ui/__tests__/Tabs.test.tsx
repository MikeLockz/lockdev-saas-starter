import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../tabs";

describe("Tabs", () => {
  it("renders complete tabs structure", () => {
    const { asFragment } = render(
      <Tabs defaultValue="account">
        <TabsList>
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="password">Password</TabsTrigger>
        </TabsList>
        <TabsContent value="account">Account settings content</TabsContent>
        <TabsContent value="password">Password settings content</TabsContent>
      </Tabs>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders tabs with disabled trigger", () => {
    const { asFragment } = render(
      <Tabs defaultValue="active">
        <TabsList>
          <TabsTrigger value="active">Active</TabsTrigger>
          <TabsTrigger value="disabled" disabled>
            Disabled
          </TabsTrigger>
        </TabsList>
        <TabsContent value="active">Active content</TabsContent>
        <TabsContent value="disabled">Disabled content</TabsContent>
      </Tabs>,
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders tabs list only", () => {
    const { asFragment } = render(
      <Tabs defaultValue="tab1">
        <TabsList>
          <TabsTrigger value="tab1">Tab 1</TabsTrigger>
          <TabsTrigger value="tab2">Tab 2</TabsTrigger>
          <TabsTrigger value="tab3">Tab 3</TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
