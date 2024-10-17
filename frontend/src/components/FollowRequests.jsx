import '../styles/components/FollowRequests.css';
import { Check, Clear } from '@mui/icons-material';

const FollowRequests = () => {
  return (
    <div className="follow-requests-column">
      <div className="requests-title">Requests</div>
      <div className="follow-request-box">
        <div className="follower-name">Test user</div>
        <div className="btns">
          <button className="reject-button">
            <Clear className="icon" />
          </button>
          <button className="accept-button">
            <Check className="icon" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FollowRequests;
