import { useQuery } from "@tanstack/react-query";
import { getWindCompare } from "../api/windApi";

export function useWindCompare(start, end, resolution) {
  return useQuery({
    queryKey: ["windCompare", start, end, resolution],
    queryFn: () => getWindCompare(start, end, resolution),
    enabled: Boolean(start && end),
  });
}
