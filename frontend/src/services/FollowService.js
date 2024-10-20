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

// URL: service/api/authors/<str:author_id>/followers/<str:follower_id>/
// based on the requird format of API , service/api/... service at the front.
export const acceptFollowRequest = async (authorId, followerId) => {
  try {
      const response = await api.put(`http://localhost:8000/service/api/authors/${authorId}/followers/${followerId}/`);  // use absolute URL
      return response.data;
  } catch (error) {
      console.error("Error accepting follow request:", error);
  }
};

export const rejectFollowRequest = async (authorId, followerId) => {
  try {
      await api.delete(`http://localhost:8000/service/api/authors/${authorId}/followers/${followerId}/`);  // use absolute URL
  } catch (error) {
      console.error("Error rejecting follow request:", error);
  }
};








