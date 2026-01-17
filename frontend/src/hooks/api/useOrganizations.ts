import api from "@/lib/axios";
import { useQuery } from "@tanstack/react-query";

export const useOrganizations = () => {
  return useQuery({
    queryKey: ["organizations"],
    queryFn: async () => {
      const response = await api.get("/organizations");
      return response.data;
    },
  });
};
