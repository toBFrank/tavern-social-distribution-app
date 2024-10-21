import axios from 'axios';
import { createPost, getAllPosts } from './PostsService';
import { getAuthorProfile } from './profileService';

export const makeGithubActivityPosts = async (authorId) => {
  try {
    const username = (await getAuthorProfile(authorId)).github.split('/').pop();
    const posts = (await getAllPosts(authorId)).data;

    // 1. Get raw data from Github API
    const rawData = await getGithubActivityData(username);
    // 2. Parse date and event type
    const parsedData = rawData
      .map((event) => {
        return {
          id: event.id,
          date: new Date(event.created_at),
          type: event.type,
          repo: event.repo,
          payload: event.payload,
        };
      })
      .filter((event) => {
        return posts.every((post) => {
          return post.description !== String(event.id);
        });
      });

    // 3. Turn into strings
    const stringifiedData = getStringsFromParsedData(parsedData, username);

    for (let i = 0; i < stringifiedData.length; i++) {
      const postData = new FormData();
      postData.append('author_id', authorId);
      postData.append('title', 'Github Activity');
      postData.append('text_content', stringifiedData[i]);
      postData.append('content_type', 'text/plain');
      postData.append('visibility', 'PUBLIC');

      // add id to check if post already exists
      postData.append('description', String(parsedData[i].id));

      await createPost(authorId, postData);
    }
  } catch (error) {
    console.error(error);
  }
};

export const getGithubActivityData = async (username) => {
  try {
    const response = await axios.get(
      `https://api.github.com/users/${username}/events/public`,
      {
        headers: {
          Accept: 'application/vnd.github+json',
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error(error);
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
    let stringifiedEvent = `On ${event.date.toDateString()}, ${username} `;

    const repoName = event.repo ? event.repo.name : 'a repository';

    switch (event.type) {
      case 'PushEvent':
        if (event.payload && event.payload.commits) {
          stringifiedEvent += `made ${event.payload.commits.length} commits in ${repoName}.`;
        } else {
          stringifiedEvent += `pushed to ${repoName}.`;
        }
        break;
      case 'PullRequestEvent':
        if (event.payload && event.payload.action) {
          stringifiedEvent += `${event.payload.action} a pull request in ${repoName}.`;
        } else {
          stringifiedEvent += `did something with a pull request in ${repoName}.`;
        }
        break;
      case 'IssuesEvent':
        if (event.payload && event.payload.action) {
          stringifiedEvent += `${event.payload.action} an issue in ${repoName}.`;
        } else {
          stringifiedEvent += `did something with an issue in ${repoName}.`;
        }
        break;
      case 'CreateEvent':
        stringifiedEvent += `created a branch or tag in ${repoName}.`;
        break;
      case 'ForkEvent':
        stringifiedEvent += `forked ${repoName}.`;
        break;
      case 'PublicEvent':
        stringifiedEvent += `made ${repoName} public.`;
        break;
      default:
        stringifiedEvent += `did something in Github.`;
        break;
    }
    return stringifiedEvent;
  });

  return stringifiedData;
};

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
