export class Follow {
    constructor(summary, actor, object) {
      this.type = 'follow';
      this.summary = summary || '';
      this.actor = actor;
      this.object = object;
    }
  }