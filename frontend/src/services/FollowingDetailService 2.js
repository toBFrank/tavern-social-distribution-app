import api from './axios';


export const getFollowing = async (authorSerial) => {
    try {
      const response = await api.get(
        `/authors/${authorSerial}/following/`
      );
      return response.data;
    } catch (error) {
      console.error(error);
    }
  };
  
  