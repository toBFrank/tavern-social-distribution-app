import Cookies from 'js-cookie';  // To access cookies

const currentHost = window.location.origin; // Get host for post URL
const API_URL = `${currentHost}/api/authors/`; // Adjust the API base URL

// Function to fetch the author profile
export const getAuthorProfile = async (authorId) => {
    const accessToken = Cookies.get('access_token');

    const response = await fetch(`${API_URL}${authorId}/profile/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
        },
        credentials: 'include',  // Include credentials (cookies)
    });
    if (!response.ok) throw new Error('Failed to fetch profile data');
    return response.json();
};

// Function to update the author profile
export const updateAuthorProfile = async (authorId, profileData) => {
    const accessToken = Cookies.get('access_token');

    const response = await fetch(`${API_URL}${authorId}/profile/edit/`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
        credentials: 'include',
    });
    if (!response.ok) throw new Error('Failed to update profile');
    return response.json();
};

export const uploadProfileImage = async (authorId, formData) => {
    const response = await fetch(`${currentHost}/authors/${authorId}/upload_image/`, {
        method: 'POST',
        body: formData
    });
    return response;
};
