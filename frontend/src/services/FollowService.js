import api from "./axios";
import Cookies from "js-cookie"; // Import js-cookie

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

// URL: /api/authors/{author_id}/inbox/
export const createFollowRequest = async (authorSerial, followRequestData) => {
    try {
      const response = await api.post(
        `/authors/${authorSerial}/inbox/`,
        followRequestData
      );
      return response.data;
    } catch (error) {
      console.error(error);
    }
};