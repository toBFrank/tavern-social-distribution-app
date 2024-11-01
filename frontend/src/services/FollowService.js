import api from "./axios";
import Cookies from "js-cookie"; // Import js-cookie

// URL: api/authors/{author_id}/inbox/follow_requests/
export const getFollowRequests = async (authorSerial) => {
  const token = Cookies.get('access_token');
    try {
      const response = await api.get(
        `authors/${authorSerial}/inbox/follow_requests/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,  // Attach token to headers
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error(error);
    }
};

// URL: /api/authors/{author_id}/inbox/
export const createFollowRequest = async (authorSerial, followRequestData) => {
  const token = Cookies.get('access_token');
    try {
      const response = await api.post(
        `/authors/${authorSerial}/inbox/`,
        followRequestData,
        {
          headers: {
            Authorization: `Bearer ${token}`,  // Attach token to headers
          },
        }
      );
      return response;
    } catch (error) {
      console.error(error);
    }
};

// URL: service/api/authors/<str:author_id>/followers/<str:follower_id>/
export const checkIfFollowing = async (authorId, followerId) => {
    // Check if followerId is a follower of authorId
  const token = Cookies.get('access_token');
    try {
      const response = await api.get(
        `http://localhost:8000/service/api/authors/${authorId}/followers/${followerId}/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      return response;
    } catch (error) {
      console.error(error);
    }
};

// URL: service/api/authors/<str:author_id>/followers/<str:follower_id>/
// based on the requird format of API , service/api/... service at the front.
export const acceptFollowRequest = async (authorId, followerId) => {
  const token = Cookies.get('access_token');
  try {
      const response = await api.put(`http://localhost:8000/service/api/authors/${authorId}/followers/${followerId}/`,
        null,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );  // use absolute URL
      return response.data;
  } catch (error) {
      console.error("Error accepting follow request:", error);
  }
};

export const rejectFollowRequest = async (authorId, followerId) => {
  const token = Cookies.get('access_token');
  try {
    await api.delete(`http://localhost:8000/service/api/authors/${authorId}/followers/${followerId}/` ,
         {
          headers: {
            Authorization: `Bearer ${ token }`,
          },
        }
        
      );  // use absolute URL
  } catch (error) {
      console.error("Error rejecting follow request:", error);
  }
};







