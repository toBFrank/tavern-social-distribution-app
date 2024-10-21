import axios from "axios";

export const makeGithubActivityPosts = async (username) => {
  try {
    // 1. Get raw data from Github API
    const rawData = await getGithubActivityData(username);

    console.log(rawData);
    // 2. Parse date and event type
    const parsedData = rawData.map((event) => {
      return {
        date: new Date(event.created_at),
        type: event.type,
      };
    });
    // 3. Turn into strings
    const stringifiedData = getStringsFromParsedData(parsedData, username);

    for (let i = 0; i < stringifiedData.length; i++) {
      console.log(stringifiedData[i]);
    }
  } catch (error) {
    console.error(error);
  }
}

export const getGithubActivityData = async (username) => {
  try {
    const response = await axios.get(`https://api.github.com/users/${username}/events/public`, {
      headers: {
        Accept: "application/vnd.github+json",
      },
    });

    return response.data;
  } catch (error) {
    console.error(error);
    return [];
  }
};

export const getStringsFromParsedData = (parsedData, username) => {
  // the main events that we will handle for now
  // const eventTypes = [
  //   "PushEvent",
  //   "PullRequestEvent",
  //   "IssuesEvent",
  //   "CreateEvent",
  //   "ForkEvent",
  //   "PublicEvent",
  // ]

  const stringifiedData = parsedData.map((event) => {
    let stringifiedEvent = `On ${event.date.toDateString()}, ${username}`;

    switch (event.type) {
      case 'PushEvent':
        stringifiedEvent += `made ${event.payload.commits.length} commits in ${event.repo.name}.`
        break;
      case 'PullRequestEvent':
        stringifiedEvent += `${event.payload.action} a pull request in ${event.repo.name}.`;
        break;
      case 'IssuesEvent':
        stringifiedEvent += `${event.payload.action} an issue in ${event.repo.name}.`;
        break;
      case 'CreateEvent':
        stringifiedEvent += `created a branch or tag in ${event.repo.name}.`;
        break;
      case 'ForkEvent':
        stringifiedEvent += `forked ${event.repo.name}.`;
        break;
      case 'PublicEvent':
        stringifiedEvent += `made ${event.repo.name} public.`;
        break;
      default:
        stringifiedEvent += `did something in Github.`;
        break;
    }
    return stringifiedEvent;
  });

  return stringifiedData;
}


// TODO: handle these in future iterations
// const relevantEventTypes = [
//   'CommitCommentEvent', 
//   'DeleteEvent', 
//   'GollumEvent', 
//   'IssueCommentEvent', 
//   'MemberEvent', 
//   'PullRequestReviewEvent', 
//   'PullRequestReviewCommentEvent', 
//   'PullRequestReviewThreadEvent', 
//   'ReleaseEvent', 
//   'SponsorshipEvent', 
//   'WatchEvent'
// ];