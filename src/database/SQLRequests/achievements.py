insertAchievement = \
    "INSERT INTO achievements (name, description, levels, previewUrl, authorId, isSpecial) " \
    "VALUES (%s, %s, %s, NULL, %s, %s) " \
    "RETURNING *"

insertUserAchievement = \
    "INSERT INTO usersachievements (userId, achievementId, level, authorId) " \
    "VALUES (%s, %s, %s, %s) " \
    "RETURNING *"

# ------------------

selectAchievementById = \
    "SELECT achievements.*, (users.givenName  || ' ' || users.familyName) as authorname, users.telegram authortelegram FROM achievements " \
    "JOIN users ON achievements.authorid = users.id " \
    "WHERE achievements.id = %s"

selectAchievementUsersAchieved = \
    "SELECT users.id, users.avatarUrl, (users.givenName  || ' ' || users.familyName) as username FROM usersAchievements " \
    "JOIN users ON usersAchievements.userId = users.id " \
    "WHERE usersAchievements.achievementId = %s"

# %s for name search must be provided as: '%{}%'.format(<YOUR_VAR>)
selectAchievementBySearchName = \
    f"SELECT * FROM achievements " \
    f"WHERE LOWER(name) LIKE %s " \
    f"ORDER BY name"

selectUserAchievementsByUserid = \
    "SELECT usersachievements.*, achievements.levels, achievements.previewUrl, achievements.isSpecial FROM usersachievements " \
    "JOIN achievements on usersachievements.achievementid = achievements.id " \
    "WHERE userid = %s " \
    "ORDER BY dategotten"

# ------------------

updateAchievementById = \
    "UPDATE achievements " \
    "SET name = %s, " \
    "description = %s, " \
    "levels = %s, " \
    "previewUrl = %s, " \
    "isSpecial = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserAchievementLevelById = \
    "UPDATE usersachievements " \
    "SET level = %s," \
    "dateGotten = NOW() " \
    "WHERE id = %s " \
    "RETURNING *"

# ------------------

deleteAchievementById = \
    "DELETE FROM achievements " \
    "WHERE id = %s"

deleteUserAchievementById = \
    "DELETE FROM usersachievements " \
    "WHERE id = %s"

deleteUserAchievementByUserIdAchievementId = \
    "DELETE FROM usersachievements " \
    "WHERE userId = %s " \
    "AND achievementId = %s"
