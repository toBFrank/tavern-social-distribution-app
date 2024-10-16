export class FollowRequest {
    constructor(summary, actor, object) {
      this.type = 'follow';
      this.summary = summary || '';
      this.actor = actor;
      this.object = object;
    }
  }