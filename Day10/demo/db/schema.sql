CREATE TABLE users (
 id INTEGER PRIMARY KEY,
 email VARCHAR(254) NOT NULL UNIQUE CHECK(length(email) BETWEEN 3 AND 254),
 nickname VARCHAR(50) NOT NULL CHECK(length(trim(nickname)) BETWEEN 1 AND 50),
 password_hash VARCHAR(255) NOT NULL CHECK(length(password_hash) BETWEEN 1 AND 255),
 role VARCHAR(10) NOT NULL DEFAULT 'USER' CHECK(role IN ('USER','ADMIN')),
 session_version INTEGER NOT NULL DEFAULT 0 CHECK(session_version >= 0),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f000+00:00','now'))
);
CREATE TABLE posts (
 id INTEGER PRIMARY KEY,
 author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
 title VARCHAR(200) NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 200),
 content TEXT NOT NULL CHECK(length(trim(content)) BETWEEN 1 AND 10000),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f000+00:00','now')),
 updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f000+00:00','now'))
);
CREATE TABLE comments (
 id INTEGER PRIMARY KEY,
 post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
 author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
 content TEXT NOT NULL CHECK(length(trim(content)) BETWEEN 1 AND 2000),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f000+00:00','now'))
);
CREATE TABLE mask_rules (
 id INTEGER PRIMARY KEY,
 rule_type VARCHAR(10) NOT NULL DEFAULT 'KEYWORD' CHECK(rule_type='KEYWORD'),
 expression VARCHAR(255) NOT NULL CHECK(length(trim(expression)) BETWEEN 1 AND 255),
 created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f000+00:00','now')),
 UNIQUE(rule_type,expression)
);
CREATE INDEX idx_posts_order ON posts(created_at,id);
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_comments_post_order ON comments(post_id,created_at,id);
CREATE INDEX idx_comments_author ON comments(author_id);
