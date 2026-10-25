import { useQuery } from "@tanstack/react-query";
import { getWindMetrics } from "../api/windApi";

export function useWindMetrics(start, end, resolution) {
  return useQuery({
    queryKey: ["windMetrics", start, end, resolution],
    queryFn: () => getWindMetrics(start, end, resolution),
    enabled: Boolean(start && end),
  });
}
