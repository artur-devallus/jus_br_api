import {useMutation, useQuery} from "@tanstack/react-query";
import {api} from "@/lib/axios.ts";
import {Query, QueryImpl} from "@/models/query.ts";


export const useCreateQuery = () => {
  return useMutation({
    mutationFn: async (data: {
      term: string;
    }): Promise<Query> => {
      const cleaned = data.term.replace(/\D/g, "");
      return api.post("/v1/queries", {term: cleaned}).then((res) => new QueryImpl(res.data));
    }
  });
};

export const useQueryDetail = (query: Query | null) => {
  return useQuery({
    queryKey: ["queryDetails", query?.id],
    queryFn: async () => {
      if (!query?.id) return null;
      return api.get(`/v1/queries/${query?.id}/detailed`).then((res) => new QueryImpl(res.data));
    },
    enabled: query?.id !== undefined,
    refetchInterval: () =>
      query?.status === "running" ? 5000 : false,
  });
}