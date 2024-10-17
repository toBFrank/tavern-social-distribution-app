export class Author {
    constructor(id, host, displayName, github, profileImage, page) {
      this.type = 'author';
      this.id = id;
      this.host = host;
      this.displayName = displayName;
      this.github = github || '';
      this.profileImage = profileImage || '';
      this.page = page || '';
    }
  }