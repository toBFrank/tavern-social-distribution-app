import { Follow } from '../models/Follow'; 

export const transformFollowData = (data) => {
  return data.map(follow => new Follow(
    follow.type,
    {
      id: follow.actor.id,
      displayName: follow.actor.displayName,
      host: follow.actor.host,
      page: follow.actor.page,
      github: follow.actor.github,
      profileImage: follow.actor.profileImage,
    },
    {
      id: follow.object.id,
      displayName: follow.object.displayName,
      host: follow.object.host,
      page: follow.object.page,
      github: follow.object.github,
      profileImage: follow.object.profileImage,
    }
  ));
};