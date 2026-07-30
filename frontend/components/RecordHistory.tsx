"use client";

import { useEffect } from "react";
import { addHistoryEntry } from "@/lib/history";

export default function RecordHistory({
  treatmentId,
  treatmentName,
  city,
  hospitalType,
}: {
  treatmentId: string;
  treatmentName: string;
  city: string;
  hospitalType?: string;
}) {
  useEffect(() => {
    addHistoryEntry({ treatment_id: treatmentId, treatment_name: treatmentName, city, hospital_type: hospitalType });
  }, [treatmentId, treatmentName, city, hospitalType]);

  return null;
}
