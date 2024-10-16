import "../styles/components/FollowRequests.css"
import { Check, Clear } from "@mui/icons-material";
import React, { useState, useEffect } from 'react';


const FollowRequests = () => {
    useEffect(() => {
        fetch('http://localhost:8000/api/authors/960fdb63-6436-4b8f-a864-7be9617f7fc4/inbox/follow_requests')
          .then(response => response.json())
          .then(json => setData(json))
          .catch(error => console.error(error));
      }, []);

    return (
        <div className="follow-requests-column">
            <div className="requests-title">Requests</div>
            <div className="follow-request-box">
                <div className="follower-name">Test user</div>
                <div className="btns">
                    <button className="reject-button"><Clear className="icon"/></button>
                    <button className="accept-button"><Check className="icon"/></button>
                </div>
            </div>
        </div>

    );
};

export default FollowRequests;