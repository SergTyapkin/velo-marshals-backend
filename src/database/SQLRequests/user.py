# -----------------------
# -- Default user part --
# -----------------------
import json

_userPublicColumns = "users.id, users.tgUsername, users.tgId, users.tel, users.avatarUrl, users.givenName, users.familyName, users.middleName, users.joinedDate, users.level"

# ----- INSERTS -----
insertUser = \
    "INSERT INTO users (tgId, tgUsername, avatarUrl, email, tel, familyName, givenName, middleName) " \
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) " \
    f"RETURNING *"

insertSession = \
    "INSERT INTO sessions (userId, token, expires, ip, browser, os, geolocation) " \
    "VALUES (%s, %s, NOW() + interval '1 week' * %s, %s, %s, %s, %s) " \
    "RETURNING *"

insertSecretCode = \
    "INSERT INTO secretCodes (userId, code, type, meta, expires) " \
    "VALUES (%s, %s, %s, %s, NOW() + interval '7 days' * %s)" \
    "RETURNING *"

# ----- SELECTS -----
selectUserIdByTgId = \
    f"SELECT id FROM users " \
    "WHERE tgId = %s"

selectUserByTgUsernameOrTgId = \
    f"SELECT * FROM users " \
    "WHERE LOWER(tgUsername) = LOWER(%s) OR " \
    "tgId = %s"

selectUserById = \
    f"SELECT * FROM users " \
    "WHERE id = %s"

selectAnotherUserById = \
    f"SELECT {_userPublicColumns} FROM users " \
    "WHERE id = %s"

selectUserByEmail = \
    f"SELECT {_userPublicColumns} FROM users " \
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
    f"SELECT users.*, ip FROM sessions " \
    "JOIN users ON sessions.userId = users.id " \
    "WHERE token = %s"

def selectUsersByFilters(filters):
    search = filters.get('search', '').lower()
    order = json.loads(filters.get('order')) if filters.get('order') else []

    return \
            f"SELECT {_userPublicColumns} FROM users " \
            "WHERE " + \
            (f"LOWER(familyName || ' ' || givenName ' ' || middleName || ' ' || id) LIKE '%%{search}%%' AND " if 'search' in filters else "") + \
            "1 = 1 " \
            "ORDER BY " + f"{', '.join(order + ['id'])}"

selectSecretCodeByUserIdType = \
    "SELECT * FROM secretCodes " \
    "WHERE userId = %s AND " \
    "type = %s AND " \
    "expires > NOW()"

selectSecretCodeByCodeType = \
    "SELECT * FROM secretCodes " \
    "WHERE code = %s AND " \
    "type = %s AND " \
    "expires > NOW()"

# ----- UPDATES -----
updateUserTgDataById = \
    "UPDATE users SET " \
    "tgId = %s, " \
    "tgUsername = %s, " \
    "avatarUrl = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserTgDataWithoutAvatarUrlById = \
    "UPDATE users SET " \
    "tgId = %s, " \
    "tgUsername = %s " \
    "WHERE id = %s " \
    "RETURNING *"

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

adminUpdateUserById = \
    "UPDATE users SET " \
    "givenName = %s, " \
    "familyName = %s, " \
    "middleName = %s, " \
    "email = %s, " \
    "tel = %s, " \
    "avatarUrl = %s, " \
    "level = %s, " \
    "tgUsername = %s, " \
    "tgId = %s, " \
    "canEditAchievements = %s, " \
    "canAssignAchievements = %s, " \
    "canEditRegistrations = %s, " \
    "canEditEvents = %s, " \
    "canEditUsersData = %s, " \
    "canEditDocs = %s, " \
    "canExecuteSQL = %s, " \
    "canEditHistory = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserConfirmationBySecretcodeType = \
    "UPDATE users " \
    "SET isConfirmedEmail = True " \
    "FROM secretCodes " \
    "WHERE secretCodes.userId = CAST(users.id as TEXT) AND " \
    "secretCodes.code = %s AND " \
    "secretCodes.type = %s " \
    "RETURNING users.*"

updateUserRevokeEmailConfirmationByUserId = \
    "UPDATE users " \
    "SET isConfirmedEmail = False " \
    "WHERE id = %s " \
    "RETURNING *"

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

deleteExpiredSecretCodes = \
    "DELETE FROM secretCodes " \
    "WHERE expires <= NOW()"

deleteSecretCodeByUseridCode = \
    "DELETE FROM secretCodes " \
    "WHERE userId = %s AND " \
    "code = %s"

deleteSecretCodeByCodeType = \
    "DELETE FROM secretCodes " \
    "WHERE code = %s AND " \
    "type = %s"
