import json

from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *

from src.database.SQLRequests import achievements as SQLAchievements


app = Blueprint('achievements', __name__)


@app.route("")
@login_required_return_id
def achievementsGet(userId_logined):
    try:
        req = request.args
        id = req.get('id')
        search = req.get('search')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if id is not None:  # get single achievement
        achievementData = DB.execute(SQLAchievements.selectAchievementById, [id])
        usersAchieved = DB.execute(SQLAchievements.selectAchievementUsersAchieved, [id], manyResults=True)
        achievementData['usersachieved'] = usersAchieved
        return jsonResponse(achievementData)

    if search is None: search = ''

    # get all achievements list
    achievements = DB.execute(SQLAchievements.selectAchievementBySearchName, ['%{}%'.format(search)], manyResults=True)
    return jsonResponse({"achievements": achievements})


@app.route("", methods=["POST"])
@login_and_can_edit_achievements_required
def achievementCreate(userData):
    try:
        req = request.json
        name = req['name']
        description = req.get('description')
        levels = req['levels']
        isSpecial = req['isSpecial']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    achievement = DB.execute(SQLAchievements.insertAchievement, [name, description, levels, userData['id'], isSpecial])

    insertHistory(
        userData['id'],
        'achievement',
        f'Creates achievement: "{achievement["name"]}" #{achievement["id"]}'
    )

    return jsonResponse(achievement)


@app.route("", methods=["PUT"])
@login_and_can_edit_achievements_required
def achievementUpdate(userData):
    try:
        req = request.json
        id = req['id']
        name = req.get('name')
        description = req.get('description')
        levels = req.get('levels')
        previewUrl = req.get('previewUrl')
        isSpecial = req.get('isSpecial')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    achievementData = DB.execute(SQLAchievements.selectAchievementById, [id])
    if achievementData is None:
        return jsonResponse("Достижение не найдено", HTTP_NOT_FOUND)

    if name is None: name = achievementData['name']
    if description is None: description = achievementData['description']
    if levels is None: levels = achievementData['levels']
    if previewUrl is None and 'previewUrl' not in req: previewUrl = achievementData['previewUrl']
    if isSpecial is None: isSpecial = achievementData['isSpecial']

    achievement = DB.execute(SQLAchievements.updateAchievementById, [name, description, levels, previewUrl, isSpecial, id])

    insertHistory(
        userData['id'],
        'achievement',
        f'Batch update achievement: {json.dumps(req)}'
    )

    return jsonResponse(achievement)


@app.route("", methods=["DELETE"])
@login_and_can_edit_achievements_required
def achievementDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(SQLAchievements.deleteAchievementById, [id])

    insertHistory(
        userData['id'],
        'achievement',
        f'Delete achievement: #{id}'
    )

    return jsonResponse("Достижение удалено")


# ---- USERS ACHIEVEMENTS

@app.route("/user")
@login_required_return_id
def userAchievementsGet(userId_logined):
    try:
        req = request.args
        userId = req['userId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    userAchievements = DB.execute(SQLAchievements.selectUserAchievementsByUserid, [userId], manyResults=True)
    list_times_to_str(userAchievements)
    return jsonResponse({"achievements": userAchievements})


@app.route("/user", methods=["POST"])
@login_and_can_assign_achievements_required
def userAchievementCreate(userData):
    try:
        req = request.json
        userId = req['userId']
        achievementId = req['achievementId']
        level = req['level']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    userAchievements = DB.execute(SQLAchievements.selectUserAchievementsByUserid, [userId], manyResults=True)
    for ach in userAchievements:  # delete another levels of this achievement
        if (ach['userid'] == userId) and (ach['achievementid'] == achievementId):
            DB.execute(SQLAchievements.deleteUserAchievementById, [ach['id']])
    achievement = DB.execute(SQLAchievements.insertUserAchievement, [userId, achievementId, level, userData['id']])

    insertHistory(
        userId,
        'achievement',
        f'Takes achievement by user #{userData["id"]}: #{achievementId}, level {level}'
    )

    return jsonResponse(achievement)


@app.route("/user", methods=["PUT"])
@login_and_can_assign_achievements_required
def userAchievementUpdate(userData):
    try:
        req = request.json
        id = req['id']
        level = req['level']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    achievement = DB.execute(SQLAchievements.updateUserAchievementLevelById, [level, id])

    insertHistory(
        achievement['userid'],
        'achievement',
        f'Takes new achievement level by user #{userData["id"]}: #{achievement["achievementid"]}, level {level}'
    )

    return jsonResponse(achievement)


@app.route("/user", methods=["DELETE"])
@login_and_can_assign_achievements_required
def userAchievementDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(SQLAchievements.deleteUserAchievementById, [id])

    insertHistory(
        userData["id"],
        'achievement',
        f'Removes achievement on user: #{id}'
    )

    return jsonResponse("Достижение пользователя удалено")
