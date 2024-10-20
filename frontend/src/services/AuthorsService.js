import api from "./axios";

// URL: ://service/api/authors/
export const getAuthors = async () => {
    try {
      const response = await api.get(
        `authors/`
      );
      return response.data;
    } catch (error) {
      console.error(error);
    }
  };