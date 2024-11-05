import api from './axios';


export const getFollowers = async (authorSerial) => {
    try {
      const response = await api.get(
        `/authors/${authorSerial}/followers/`
      );
      return response.data;
    } catch (error) {
      console.error(error);
    }
  };
  
  