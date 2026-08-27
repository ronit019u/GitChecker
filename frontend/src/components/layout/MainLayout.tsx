import { useState } from "react";
import { Navbar } from "./Navbar";
import { Outlet } from "react-router-dom";
import type { HistoryData } from "@/types/types";

export const MainLayout = () => {
  const [selectedHistoryItem, setSelectedHistoryItem] =
    useState<HistoryData | null>(null);
  return (
    <div>
      <Navbar onSelectedHistory={setSelectedHistoryItem} />
      <Outlet
        context={{
          selectedHistoryItem,
          clearSelectedHistoryItem: () => setSelectedHistoryItem(null),
        }}
      />
    </div>
  );
};
