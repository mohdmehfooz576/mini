CREATE DATABASE IF NOT EXISTS voteright;

USE voteright;


-- ==========================================
-- USERS TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    role ENUM('admin', 'voter')
        NOT NULL DEFAULT 'voter',

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- VOTERS TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS voters (

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL UNIQUE,

    roll_no VARCHAR(50) NOT NULL UNIQUE,

    mobile VARCHAR(20),

    department VARCHAR(100),

    year VARCHAR(50),

    status ENUM(
        'Pending',
        'Approved',
        'Rejected'
    ) DEFAULT 'Pending',

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- ==========================================
-- ELECTIONS TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS elections (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(150) NOT NULL,

    description TEXT,

    start_date DATE NOT NULL,

    end_date DATE NOT NULL,

    status ENUM(
        'Active',
        'Stopped'
    ) DEFAULT 'Active',

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- CANDIDATES TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS candidates (

    id INT AUTO_INCREMENT PRIMARY KEY,

    election_id INT NOT NULL,

    name VARCHAR(100) NOT NULL,

    year_position VARCHAR(100),

    vote_count INT DEFAULT 0,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (election_id)
        REFERENCES elections(id)
        ON DELETE CASCADE
);


-- ==========================================
-- VOTES TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS votes (

    id INT AUTO_INCREMENT PRIMARY KEY,

    voter_id INT NOT NULL,

    election_id INT NOT NULL,

    candidate_id INT NOT NULL,

    voted_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (voter_id)
        REFERENCES voters(id)
        ON DELETE CASCADE,

    FOREIGN KEY (election_id)
        REFERENCES elections(id)
        ON DELETE CASCADE,

    FOREIGN KEY (candidate_id)
        REFERENCES candidates(id)
        ON DELETE CASCADE,

    UNIQUE KEY unique_voter_election
    (
        voter_id,
        election_id
    )
);