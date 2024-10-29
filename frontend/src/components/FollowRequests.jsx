import "../styles/components/FollowRequests.css";
import { Check, Clear } from "@mui/icons-material";
import React, { useState, useEffect } from 'react';
import { transformFollowData } from "../utils/transformer";
import { getFollowRequests } from '../services/FollowService';
import { acceptFollowRequest, rejectFollowRequest } from '../services/FollowService';
import Cookies from 'js-cookie';

const FollowRequests = () => {
    const [followRequests, setFollowRequests] = useState([]);
    const authorId = Cookies.get('author_id');

    useEffect(() => {
        const fetchFollowRequests = async () => {
            // Fetch follow requests for the author
            try {
                const response = await getFollowRequests(authorId);
                setFollowRequests(transformFollowData(response));
            } catch (error) {
                console.error(error);
            }
        };

        fetchFollowRequests();
    }, [authorId]);

    const handleAccept = async (followerId) => {
        // Accept follow request
        try {
            await acceptFollowRequest(authorId, followerId);
            setFollowRequests(prevRequests => prevRequests.filter(request => request.actor.id !== followerId));
        } catch (error) {
            console.error(error);
        }
    };

    const handleReject = async (followerId) => {
        // Deny follow request
        try {
            await rejectFollowRequest(authorId, followerId);
            setFollowRequests(prevRequests => prevRequests.filter(request => request.actor.id !== followerId));
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="FollowRequest-container">
            <div className="requests-title">Requests</div>
            {followRequests.map((followRequest, index) => {
                console.log(followRequest.actor.profileImage); 
                return (
                    <div key={index} className="follow-request-box">
                        <div className="follower-picAndName"> 
                            <img
                                className="follower-profilePic"
                                src={followRequest.actor.profileImage} 
                                alt={`Img`} 
                            />
                            <div className="follower-name">{followRequest.actor.displayName}</div>
                        </div>
                        <div className="btns">
                            <button className="reject-button" onClick={() => handleReject(followRequest.actor.id)}>
                                <Clear className="icon"/> {/* 'x' button */}
                            </button>
                            <button className="accept-button" onClick={() => handleAccept(followRequest.actor.id)}>
                                <Check className="icon"/> {/* check button */}
                            </button>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default FollowRequests;
