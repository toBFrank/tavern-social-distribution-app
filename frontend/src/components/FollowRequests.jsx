import "../styles/components/FollowRequests.css"
import { Check, Clear } from "@mui/icons-material";
import React, { useState, useEffect } from 'react';
import { transformFollowData } from "../utils/transformer";


const FollowRequests = () => {
    
    // https://builtin.com/software-engineering-perspectives/react-api how to make API requests in react with fetch 2024-10-16
    const [followRequests, setFollowRequests] = useState([]);
    const token = '7e31046a8413002b920bdc8dd0232bad6c482e1e';

    useEffect(() => {
        fetch('http://localhost:8000/api/authors/1d6dfebf-63a6-47a9-8e88-5cda73675db5/inbox/follow_requests/', {
            method: 'GET',
            headers: {
                'Authorization': `Token ${token}`, // Django REST framework needs endpoint to be authenticated??
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

    return (
        <div>
            <div className="requests-title">Requests</div>
            {followRequests.map((followRequest, index) => (
                <div key={index} className="follow-request-box">
                <div className="follower-name">{followRequest.actor.displayName}</div>
                <div className="btns">
                    <button className="reject-button"><Clear className="icon"/></button>
                    <button className="accept-button"><Check className="icon"/></button>
                </div>
            </div>
            ))}
        </div>
    );
};

export default FollowRequests;
