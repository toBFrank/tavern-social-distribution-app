import api from './axios';

// URL: ://service/api/authors/{AUTHOR_SERIAL}/inbox
export const createComment = async (authorSerial, postSerial, commentData) => {
  try {
    const response = await api.post(
      `/authors/${authorSerial}/inbox`,
      commentData
    );
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: api/authors/<uuid:author_serial>/commented/
export const createCommentLocal = async (authorSerial, commentData) => {
  try {
    const response = await api.post(
      `/authors/${authorSerial}/commented/`,
      commentData
    );
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/authors/{AUTHOR_SERIAL}/posts/{POST_SERIAL}/comments
export const getComments = async (authorSerial, postSerial) => {
  try {
    const response = await api.get(
      `/authors/${authorSerial}/posts/${postSerial}/comments/`
    );
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/posts/{POST_FQID}/comments
export const getCommentsByFqid = async (postFqid) => {
  try {
    const response = await api.get(`/posts/${postFqid}/comments`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/authors/{AUTHOR_SERIAL}/post/{POST_SERIAL}/comment/{REMOTE_COMMENT_FQID}
export const getCommentRemote = async (
  authorSerial,
  postSerial,
  remoteCommentFqid
) => {
  try {
    const response = await api.get(
      `/authors/${authorSerial}/post/${postSerial}/comment/${remoteCommentFqid}`
    );
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/comment/{COMMENT_FQID}
export const getComment = async (commentFqid) => {
  try {
    const response = await api.get(`/comment/${commentFqid}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/authors/{AUTHOR_SERIAL}/commented
export const getAuthorComments = async (authorSerial) => {
  try {
    const response = await api.get(`/authors.${authorSerial}/commented`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/authors/{AUTHOR_FQID}/commented
export const getAuthorCommentsByFqid = async (authorFqid) => {
  try {
    const response = await api.get(`/authors/${authorFqid}/commented`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/authors/{AUTHOR_SERIAL}/commented/{COMMENT_SERIAL}
export const getAuthorComment = async (authorSerial, commentSerial) => {
  try {
    const response = await api.get(
      `/authors/${authorSerial}/commented/${commentSerial}`
    );
    return response.data;
  } catch (error) {
    console.error(error);
  }
};

// URL: ://service/api/commented/{COMMENT_FQID}
export const getCommentedByFqid = async (commentFqid) => {
  try {
    const response = await api.get(`/commented/${commentFqid}`);
    return response.data;
  } catch (error) {
    console.error(error);
  }
};
