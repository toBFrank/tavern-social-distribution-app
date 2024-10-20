import "../styles/components/FollowRequests.css";
import { Check, Clear } from "@mui/icons-material";
import React, { useState, useEffect } from 'react';
import { transformFollowData } from "../utils/transformer";
import { getFollowRequests } from '../services/FollowService';
import Cookies from 'js-cookie';

const FollowRequests = () => {
    const [followRequests, setFollowRequests] = useState([]);
    const authorId = Cookies.get('author_id');

    useEffect(() => {
        const fetchFollowRequests = async () => { //make request for follow requests for author
            try {
                const response = await getFollowRequests(authorId);
                setFollowRequests(transformFollowData(response));
            } catch (error) {
                console.error(error);
            }
        };

        fetchFollowRequests();
    }, [authorId]);

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