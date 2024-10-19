export const getAuthorProfile = async (authorId) => {

    try {
        const response = await fetch(`http://localhost:8000/authors/${authorId}/profile/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
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

