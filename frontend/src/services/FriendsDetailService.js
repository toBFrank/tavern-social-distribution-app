import api from './axios';


export const getFriends = async (authorSerial) => {
    try {
      const response = await api.get(
        `/authors/${authorSerial}/friends/`
      );
      return response.data;
    } catch (error) {
      console.error(error);
    }
  };
  
  