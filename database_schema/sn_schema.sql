-- Used https://dbml.dbdiagram.io to generate PNG for database schema 2024-10-03

CREATE TABLE "Author" (
  "id" varchar PRIMARY KEY, -- full API url for author http://nodeaaaa/api/authors/111
  "host" varchar, -- full API URL for author's node
  "displayName" varchar, -- how use would like name to be displayed
  "github" varchar, -- URL of user's  github
  "profileImage" varchar, -- URL of user's profile image
  "page" varchar --  URL of user's HTML profile page http://nodeaaaa/api/authors/greg
);

-- https://stackoverflow.com/questions/68889357/designing-a-follower-following-schema-between-two-tables-in-sql for how to manage followers 2024-10-03
CREATE TABLE "Follows" (
  -- Amy is following Bret
  "author_id_follower" varchar, -- Amy is following
  "author_id_followee" varchar -- Bret is being followed
);

CREATE TABLE "Post" (
  "id" varchar PRIMARY KEY, -- original URL on node post came from http://nodebbbb/api/authors/222/posts/249 
  "author_id" varchar, -- id of author who CREATED the post
  "title" varchar,
  "description" varchar,
  "contentType" varchar,
  "content" varchar,
  "published" timestamp,
  "visibility" varchar -- FRIENDS, PUBLIC, or UNLISTED
);

CREATE TABLE "Comment" (
  "id" varchar PRIMARY KEY, -- id of the comment http://nodeaaaa/api/authors/111/commented/130
  "author_id" varchar, -- id of author who WROTE the comment
  "post" varchar, -- id of post http://nodebbbb/api/authors/222/posts/249 
  "comment" varchar,
  "contentType" varchar,
  "published" timestamp,
  "page" varchar -- may or may not be the same as page for post,
  -- depending on if there's a seperate URL to just see the one comment in html
);

CREATE TABLE "Like" (
  "id" varchar PRIMARY KEY, -- http://nodeaaaa/api/authors/111/liked/166 
  "author_id" varchar, -- author that made the like
  "published" timestamp,
  "object" varchar -- the URL of the object that was liked (so url of comment or post)
  --e.g. http://nodeaaaa/api/authors/111/commented/130 or http://nodebbbb/authors/222/posts/249
);

-- foreign keys
ALTER TABLE "Follows" ADD FOREIGN KEY ("author_id_follower") REFERENCES "Author" ("id");

ALTER TABLE "Follows" ADD FOREIGN KEY ("author_id_followee") REFERENCES "Author" ("id");

ALTER TABLE "Post" ADD FOREIGN KEY ("author_id") REFERENCES "Author" ("id");

ALTER TABLE "Comment" ADD FOREIGN KEY ("post") REFERENCES "Post" ("id");

ALTER TABLE "Comment" ADD FOREIGN KEY ("author_id") REFERENCES "Author" ("id");

ALTER TABLE "Like" ADD FOREIGN KEY ("author_id") REFERENCES "Author" ("id");

-- indexes
CREATE INDEX "idx_host" ON "Author" ("host"); -- differentiate between local authors and remote authors

CREATE INDEX "idx_visibility" ON "Post" ("visibility"); -- many instances where we need to search by visibility (POST API, Comments API...)