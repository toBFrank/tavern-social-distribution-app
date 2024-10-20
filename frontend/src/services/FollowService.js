import api from "./axios";

// URL: api/authors/{author_id}/inbox/follow_requests/
export const getFollowRequests = async (authorSerial) => {
    try {
      const response = await api.get(
        `authors/${authorSerial}/inbox/follow_requests/`
      );
      return response.data;
    } catch (error) {
      console.error(error);
    }
  };