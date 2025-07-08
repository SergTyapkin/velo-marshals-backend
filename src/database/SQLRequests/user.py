# -----------------------
# -- Default user part --
# -----------------------
_userColumns = "users.id, users.tgUsername, users.tgId, users.email, users.tel, users.avatarUrl, users.givenName, users.familyName, users.middleName, users.joinedDate, users.level, users.canEditAchievements, users.canAssignAchievements, users.canEditRegistrations, users.canEditEvents, users.canEditUsersLevels, users.canEditUsersData, users.canEditDocs, users.canExecuteSQL"

# ----- INSERTS -----
insertUser = \
    "INSERT INTO users (password, avatarUrl, email, firstName, secondName, thirdName, telegram) " \
    "VALUES (%s, NULL, %s, %s, %s, %s, %s) " \
    f"RETURNING {_userColumns}"

insertSession = \
    "INSERT INTO sessions (userId, token, expires, ip, browser, os, geolocation) " \
    "VALUES (%s, %s, NOW() + interval '1 week' * %s, %s, %s, %s, %s) " \
    "RETURNING *"

# ----- SELECTS -----
selectUserByEmailPassword = \
    f"SELECT {_userColumns} FROM users " \
    "WHERE email = %s AND password = %s"

selectUserById = \
    f"SELECT {_userColumns} FROM users " \
    "WHERE id = %s"

selectAnotherUserById = \
    f"SELECT id, firstName, secondName, thirdName, joinedDate, avatarUrl, telegram, title FROM users " \
    "WHERE id = %s"

selectAnotherUserByIdWithEmail = \
    f"SELECT id, firstName, secondName, thirdName, joinedDate, avatarUrl, telegram, title, email, isConfirmedEmail FROM users " \
    "WHERE id = %s"

selectUserByEmail = \
    f"SELECT {_userColumns} FROM users " \
    "WHERE email = %s"

selectUserIdBySessionToken = \
    "SELECT userId, ip FROM sessions " \
    "WHERE token = %s"

selectSessionByUserId = \
    "SELECT token, expires FROM sessions " \
    "WHERE userId = %s"

selectAllUserSessions = \
    "SELECT token, expires, ip, browser, os, geolocation FROM sessions " \
    "WHERE userId = %s"

selectUserDataBySessionToken = \
    f"SELECT {_userColumns}, ip FROM sessions " \
    "JOIN users ON sessions.userId = users.id " \
    "WHERE token = %s"

def selectUsersByFilters(filters):
    return \
            f"SELECT {_userColumns} FROM users " \
            "WHERE " + \
            (f"isconfirmedByAdmin = {filters['confirmedByAdmin']} AND " if 'confirmedByAdmin' in filters else "") + \
            (f"isconfirmedEmail = {filters['confirmedEmail']} AND " if 'confirmedEmail' in filters else "") + \
            (
                f"LOWER(firstName  || ' ' || secondName) LIKE '%%{filters['search'].lower()}%%' AND " if 'search' in filters else "") + \
            "1 = 1 " \
            "ORDER BY firstName, secondName"


selectRegistrationsExtractByUserIdDatestartDateend = \
    "SELECT events.*, events.date FROM registrations " \
    "JOIN events ON registrations.eventid = events.id " \
    "WHERE userid = %s " \
    "AND events.date BETWEEN %s AND %s"

# ----- UPDATES -----
updateUserById = \
    "UPDATE users SET " \
    "givenName = %s, " \
    "familyName = %s, " \
    "middleName = %s, " \
    "email = %s, " \
    "tel = %s, " \
    "avatarUrl = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserPasswordByIdPassword = \
    "UPDATE users SET " \
    "password = %s " \
    "WHERE id = %s AND password = %s " \
    "RETURNING id"


# ----- DELETES -----
deleteExpiredSessions = \
    "DELETE FROM sessions " \
    "WHERE expires <= NOW()"

deleteUserById = \
    "DELETE FROM users " \
    "WHERE id = %s"

deleteSessionByToken = \
    "DELETE FROM sessions " \
    "WHERE token = %s"

deleteAllUserSessionsWithoutCurrent = \
    "DELETE FROM sessions " \
    "WHERE userId = %s AND " \
    "token != %s"
