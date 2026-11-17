import { describe, expect, it } from "vitest";
import { QueryClient } from "@tanstack/react-query";

describe("query client", () => {
  it("creates an isolated client for the mobile app", () => {
    const client = new QueryClient();

    expect(client).toBeInstanceOf(QueryClient);
    client.clear();
  });
});
