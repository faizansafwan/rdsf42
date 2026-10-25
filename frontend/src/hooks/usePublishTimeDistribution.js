import { useQuery } from "@tanstack/react-query";
import { getPublishTimeDistribution } from "../api/windApi";

export function usePublishTimeDistribution(date) {
  return useQuery({
    queryKey: ["publishTime", date],
    queryFn: () => getPublishTimeDistribution(date),
    enabled: Boolean(date),
  });
}
