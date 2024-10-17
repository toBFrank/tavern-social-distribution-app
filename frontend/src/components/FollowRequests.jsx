import "../styles/components/FollowRequests.css"
import { Check, Clear } from "@mui/icons-material";
import React, { useState, useEffect } from 'react';
import { transformFollowData } from "../utils/transformer";


const FollowRequests = () => {
    
    // https://builtin.com/software-engineering-perspectives/react-api how to make API requests in react with fetch 2024-10-16
    const [followRequests, setFollowRequests] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/authors/cb3ef4e8-e688-417e-b032-a96f359fcd54/inbox/follow_requests')
          .then(response => response.json())
          .then(json => setFollowRequests(transformFollowData(json))) //transform into Follow objects
          .catch(error => console.error(error));
      }, []);

    return (
        <div className="follow-requests-column">
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