import "../styles/components/FollowRequests.css";
import { Check, Clear } from "@mui/icons-material";
import React, { useState, useEffect } from 'react';
import { transformFollowData } from "../utils/transformer";

const FollowRequests = () => {
    const [followRequests, setFollowRequests] = useState([]);
    const token = '1efe67a71074809a52cf8e680e4bd764eb07a39f';

    useEffect(() => {
        fetch('http://localhost:8000/api/authors/73d430ba-6f7f-46fa-ba1e-03156c16bed9/inbox/follow_requests/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(json => setFollowRequests(transformFollowData(json)))
        .catch(error => console.error('Fetch error:', error));
    }, []);

    const handleReject = (id) => {
        // reject following request
        setFollowRequests(prevRequests => prevRequests.filter(request => request.id !== id));
    };

    const handleAccept = (id) => {
        // accept following request
        setFollowRequests(prevRequests => prevRequests.filter(request => request.id !== id));
        console.log(`Accepted request with id: ${id}`);
    };

    return (
        <div>
            <div className="requests-title">Requests</div>
            {followRequests.map((followRequest, index) => (
                <div key={index} className="follow-request-box">
                    <div className="follower-name">{followRequest.actor.displayName}</div>
                    <div className="btns">
                        <button className="reject-button" onClick={() => handleReject(followRequest.id)}>
                            <Clear className="icon"/> {/* 'x' button */}
                        </button>
                        <button className="accept-button" onClick={() => handleAccept(followRequest.id)}>
                            <Check className="icon"/> {/* check button */}
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default FollowRequests;
