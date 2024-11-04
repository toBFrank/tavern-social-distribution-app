import api from './axios';

// URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}
export const getPost = async (authorSerial, postSerial) => {
  try {
    const response = await api.get(
      `authors/${authorSerial}/posts/${postSerial}/`
    );
    return response;
  } catch (error) {
    throw error;
  }
};

// Update post visibility to 'DELETED' instead of actually deleting the post
export const deletePost = async (authorSerial, postSerial) => {
  try {
    // Update the post's visibility to 'DELETED' instead of deleting
    const postData = { visibility: 'DELETED' };
    const response = await api.patch(
      `posts/authors/${authorSerial}/posts/${postSerial}/`,
      postData
    );
    return response;
  } catch (error) {
    throw error;
  }
};

export const updatePost = async (authorSerial, postSerial, postData) => {
  try {
    const response = await api.put(
      `authors/${authorSerial}/posts/${postSerial}/`,
      postData
    );
    return response;
  } catch (error) {
    throw error;
  }
};

// URL: ://service/api/posts/{POST_FQID}
export const getPostByFqid = async (postFqid) => {
  try {
    const response = await api.get(`posts/${postFqid}/`);
    return response;
  } catch (error) {
    throw error;
  }
};

// URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/
export const getAllPosts = async (authorSerial) => {
  try {
    const response = await api.get(`authors/${authorSerial}/posts/`);
    return response;
  } catch (error) {
    throw error;
  }
};
export const createPost = async (authorSerial, postData) => {
  try {
    const response = await api.post(
      `authors/${authorSerial}/posts/`,
      postData
    );
    return response;
  } catch (error) {
    throw error;
  }
};

// URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/image
export const getPostImageUrl = async (authorSerial, postSerial) => {
  try {
    const response = await api.get(
      `authors/${authorSerial}/posts/${postSerial}/image/`,
      { responseType: 'blob' }
    );

    const imageUrl = URL.createObjectURL(response.data);
    return imageUrl;
  } catch (error) {
    throw error;
  }
};
