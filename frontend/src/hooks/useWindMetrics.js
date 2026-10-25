import { useQuery } from "@tanstack/react-query";
import { getWindMetrics } from "../api/windApi";

export function useWindMetrics(start, end) {
  return useQuery({
    queryKey: ["windMetrics", start, end],
    queryFn: () => getWindMetrics(start, end),
    enabled: Boolean(start && end),
  });
}
