export const getAuthorProfile = async (authorId, token) => {
    try {
        const response = await fetch(`http://localhost:8000/api/authors/${authorId}/profile/`, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,  // Include the token in the Authorization header
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`, // Include the token in the headers
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch profile');
        }

        return await response.json();
    } catch (error) {
        console.error(error);
        throw error;
    }
};
