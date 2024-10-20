// profileService.js

const API_URL = 'http://127.0.0.1:8000/authors/';  // Adjust the API base URL

export const getAuthorProfile = async (authorId) => {
    const response = await fetch(`${API_URL}${authorId}/profile/`);
    if (!response.ok) throw new Error('Failed to fetch profile data');
    return response.json();
};

export const updateAuthorProfile = async (authorId, profileData) => {
    const response = await fetch(`${API_URL}${authorId}/profile/edit/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
    });
    if (!response.ok) throw new Error('Failed to update profile');
    return response.json();
};
