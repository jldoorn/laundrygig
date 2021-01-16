CREATE TABLE IF NOT EXISTS person(
    user INTEGER PRIMARY KEY AUTOINCREMENT,
    room INTEGER NOT NULL,
    building TEXT NOT NULL,
    fname TEXT,
    lname TEXT,
    puid TEXT,
    email TEXT
);
CREATE TABLE IF NOT EXISTS active_job(
    id INTEGER PRIMARY KEY,
    requester INTEGER,
    worker INTEGER,
    bags INTEGER,
    request_time INTEGER,
    start_time INTEGER,
    load_charge INTEGER,

    FOREIGN KEY (requester) REFERENCES person(user) ON DELETE CASCADE,
    FOREIGN KEY (worker) REFERENCES person(user) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS pending_job(
    id INTEGER PRIMARY KEY,
    requester INTEGER,
    bags INTEGER,
    request_time INTEGER,
    FOREIGN KEY (requester) REFERENCES person(user) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS completed_job(
    id INTEGER PRIMARY KEY,
    requester INTEGER,
    worker INTEGER,
    bags INTEGER,
    request_time INTEGER,
    start_time INTEGER,
    end_time INTEGER,
    load_charge INTEGER,
    gig_pay INTEGER,
    commission INTEGER,

    FOREIGN KEY (requester) REFERENCES person(user) ON DELETE CASCADE,
    FOREIGN KEY (worker) REFERENCES person(user) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS credit(
    id INTEGER PRIMARY KEY,
    user INTEGER,
    balance REAL,

    FOREIGN KEY (user) references person(user) ON DELETE CASCADE
);