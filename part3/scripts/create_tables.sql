-- ============================================================
-- HBnB - Table Creation Script
-- ============================================================

-- 1. Users table
CREATE TABLE IF NOT EXISTS users (
    id         CHAR(36) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name  VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    is_admin   BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Amenities table
CREATE TABLE IF NOT EXISTS amenities (
    id         CHAR(36) PRIMARY KEY,
    name       VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Places table (depends on users)
CREATE TABLE IF NOT EXISTS places (
    id          CHAR(36) PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    price       DECIMAL(10, 2) NOT NULL,
    latitude    FLOAT NOT NULL,
    longitude   FLOAT NOT NULL,
    owner_id    CHAR(36) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- 4. Reviews table (depends on users and places)
CREATE TABLE IF NOT EXISTS reviews (
    id         CHAR(36) PRIMARY KEY,
    text       TEXT NOT NULL,
    rating     INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    user_id    CHAR(36) NOT NULL,
    place_id   CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)  REFERENCES users(id),
    FOREIGN KEY (place_id) REFERENCES places(id),
    UNIQUE (user_id, place_id)
);

-- 5. Place_Amenity table (depends on places and amenities)
CREATE TABLE IF NOT EXISTS place_amenity (
    place_id   CHAR(36) NOT NULL,
    amenity_id CHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id)   REFERENCES places(id),
    FOREIGN KEY (amenity_id) REFERENCES amenities(id)
);
