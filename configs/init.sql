------- Users data -------
CREATE TABLE IF NOT EXISTS users (
    id               SERIAL PRIMARY KEY,
    tgUsername       TEXT DEFAULT NULL UNIQUE,
    tgId             TEXT DEFAULT NULL UNIQUE,
    email            TEXT DEFAULT NULL UNIQUE,
    isConfirmedEmail BOOLEAN NOT NULL DEFAULT FALSE,
    tel              TEXT DEFAULT NULL UNIQUE,
    avatarUrl        TEXT DEFAULT NULL,
    familyName       TEXT DEFAULT NULL,
    givenName        TEXT DEFAULT NULL,
    middleName       TEXT DEFAULT NULL,
    joinedDate       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    level            INTEGER NOT NULL DEFAULT 1,

    canEditAchievements     BOOLEAN DEFAULT FALSE,
    canAssignAchievements   BOOLEAN DEFAULT FALSE,
    canEditRegistrations    BOOLEAN DEFAULT FALSE,
    canEditEvents           BOOLEAN DEFAULT FALSE,
    canEditUsersData        BOOLEAN DEFAULT FALSE,
    canEditDocs             BOOLEAN DEFAULT FALSE,
    canExecuteSQL           BOOLEAN DEFAULT FALSE,
    canEditHistory          BOOLEAN DEFAULT FALSE,
    canEditGlobals          BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS sessions (
    userId   SERIAL NOT NULL REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    token    TEXT NOT NULL UNIQUE,
    expires  TIMESTAMP WITH TIME ZONE,
    ip          TEXT,
    browser     TEXT,
    os          TEXT,
    geolocation TEXT
);

CREATE TABLE IF NOT EXISTS secretCodes (
    id             SERIAL PRIMARY KEY,
    userId         TEXT NOT NULL,
    code           TEXT NOT NULL UNIQUE,
    type           TEXT NOT NULL,
    meta           TEXT DEFAULT NULL,
    expires        TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE (userId, type)
);

------ Events data -------
CREATE TABLE IF NOT EXISTS events (
    id                   SERIAL PRIMARY KEY,
    title                TEXT NOT NULL DEFAULT '',
    description          TEXT NOT NULL DEFAULT '',
    fullDescription      TEXT NOT NULL DEFAULT '',
    routeDescription     TEXT NOT NULL DEFAULT '',
    createdDate          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    startDate            TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NULL,
    cameDate             TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NULL,
    previewUrl           TEXT DEFAULT NULL,
    customCSS            TEXT DEFAULT NULL,
    lapDistanceKm        FLOAT NOT NULL,
    medalPreviewUrl      TEXT DEFAULT NULL,
    isRegistrationOpened BOOLEAN NOT NULL DEFAULT FALSE,
    authorId             INT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS registrations (
    id           SERIAL PRIMARY KEY,
    userId       INT NOT NULL REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    eventId      INT NOT NULL REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE,
    isConfirmed  BOOLEAN DEFAULT NULL,
    userComment  TEXT DEFAULT NULL,
    adminComment TEXT DEFAULT NULL,
    level        INT DEFAULT NULL,
    salary       INT DEFAULT NULL,
    taskText     TEXT DEFAULT NULL,
    cameDate     TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    leaveDate    TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    lapsPassed   FLOAT NOT NULL DEFAULT 0,
    UNIQUE (userId, eventId)
);

------ Equipment data ------
CREATE TABLE IF NOT EXISTS equipment (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    description     TEXT DEFAULT NULL,
    previewUrl      TEXT DEFAULT NULL,
    amountTotal     INT NOT NULL,
    isNeedsToReturn BOOLEAN NOT NULL,
    eventId         INT NOT NULL REFERENCES events(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS usersEquipments (
    id             SERIAL PRIMARY KEY,
    userId         INT NOT NULL REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    equipmentId    INT NOT NULL REFERENCES equipment(id) ON DELETE CASCADE ON UPDATE CASCADE,
    amountHolds    INT NOT NULL,
    takenDate      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updatedDate    TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    UNIQUE (userId, equipmentId)
);

------- Achievements data -------
CREATE TABLE IF NOT EXISTS achievements (
    id             SERIAL PRIMARY KEY,
    name           TEXT NOT NULL,
    description    TEXT DEFAULT NULL,
    levels         INT NOT NULL,
    previewUrl     TEXT DEFAULT NULL,
    isSpecial      BOOLEAN NOT NULL DEFAULT FALSE,
    authorId       INT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS usersAchievements (
    id             SERIAL PRIMARY KEY,
    userId         INT REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    achievementId  INT REFERENCES achievements(id) ON DELETE CASCADE ON UPDATE CASCADE,
    level          INT NOT NULL DEFAULT 1,
    gottenDate     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    authorId       INT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE (userId, achievementId)
);

------- Docs -------
CREATE TABLE IF NOT EXISTS docs (
    id             SERIAL PRIMARY KEY,
    title          TEXT NOT NULL,
    text           TEXT NOT NULL,
    createdDate    TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    editedDate     TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    authorId       INT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    lastRedactorId INT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
);

------ Images ------
CREATE TABLE IF NOT EXISTS images (
    id             SERIAL PRIMARY KEY,
    author         INT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    type           TEXT NOT NULL,
    bytes          BYTEA
);

------ Total history ------
CREATE TABLE IF NOT EXISTS history (
    id             SERIAL PRIMARY KEY,
    userId         INT REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    type           TEXT NOT NULL,
    text           TEXT NOT NULL,
    date           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

------ Globals ------
CREATE TABLE IF NOT EXISTS globals (
    inEventId       INT REFERENCES events(id) ON DELETE SET NULL ON UPDATE CASCADE DEFAULT NULL,
    isOnMaintenance BOOLEAN NOT NULL DEFAULT FALSE
);
