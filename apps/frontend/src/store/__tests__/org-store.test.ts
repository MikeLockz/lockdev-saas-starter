import { beforeEach, describe, expect, it } from "vitest";
import { useOrgStore } from "../org-store";

describe("Org Store", () => {
  beforeEach(() => {
    // Reset store state before each test
    useOrgStore.setState({ currentOrgId: null });
  });

  it("has correct initial state", () => {
    const state = useOrgStore.getState();
    // Snapshot only serializable state, not functions
    expect({
      currentOrgId: state.currentOrgId,
    }).toMatchSnapshot();
  });

  it("state after selecting an organization", () => {
    const { setCurrentOrgId } = useOrgStore.getState();
    setCurrentOrgId("org-123-abc");

    const state = useOrgStore.getState();
    expect({
      currentOrgId: state.currentOrgId,
    }).toMatchSnapshot();
  });

  it("state after clearing organization", () => {
    const { setCurrentOrgId } = useOrgStore.getState();
    // First set an org
    setCurrentOrgId("org-123-abc");
    // Then clear it
    setCurrentOrgId(null);

    const state = useOrgStore.getState();
    expect({
      currentOrgId: state.currentOrgId,
    }).toMatchSnapshot();
  });
});
