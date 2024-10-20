import api from "./axios";
import Cookies from "js-cookie"; // Import js-cookie

// URL: api/authors/{author_id}/inbox/follow_requests/
export const getFollowRequests = async () => {
  try {
    // Get the author_id from the cookies
    const authorSerial = Cookies.get('author_id');

    if (!authorSerial) {
      throw new Error("Author ID is missing from cookies.");
    }

    const response = await api.get(`authors/${authorSerial}/inbox/follow_requests/`, {
      withCredentials: true
    });

    return response.data;
  } catch (error) {
    console.error("Error fetching follow requests:", error);
  }
};
