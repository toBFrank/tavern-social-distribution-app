import Cookies from 'js-cookie'; // To access cookies

export const getAuthorProfile = async (authorId) => {
    try {
        // Get the access token from cookies
        const accessToken = Cookies.get('access_token');

        if (!accessToken) {
            throw new Error('Access token is missing. Please log in.');
        }

        // Make the request with the Authorization header
        const response = await fetch(`http://localhost:8000/api/authors/${authorId}/profile/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`, // Include the access token
            },
            credentials: 'include', // Ensures cookies are sent with the request
        });

        if (!response.ok) {
            throw new Error('Failed to fetch profile');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching profile:', error);
        throw error;
    }
};
