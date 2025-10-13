import {useMutation, useQuery} from "@tanstack/react-query";
import {api} from "@/lib/axios.ts";
import {Query, QueryImpl} from "@/models/query.ts";


export const useCreateQuery = () => {
  return useMutation({
    mutationFn: async (data: {
      term: string;
      enqueue?: boolean
    }): Promise<Query> => {
      const cleaned = data.term.replace(/\D/g, "");
      return api.post("/v1/queries", {term: cleaned, enqueue: data.enqueue}).then((res) => new QueryImpl(res.data));
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

export async function runWithConcurrency<T, R>(
  items: T[],
  worker: (item: T) => Promise<R>,
  concurrency = 5,
) {
  const results: R[] = [];
  const queue = items.slice();
  const runners: Promise<void>[] = [];
  
  async function next() {
    const item = queue.shift();
    if (!item) return;
    try {
      const r = await worker(item);
      results.push(r);
    } catch (e) {
      results.push(e as unknown as R);
    }
    await next();
  }
  
  for (let i = 0; i < Math.min(concurrency, items.length); i++) {
    runners.push(next());
  }
  await Promise.all(runners);
  return results;
}
