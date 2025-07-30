import json
import uuid

from flask import Blueprint

from src.connections import config

from src.utils.access import *
from src.constants import *
from src.utils.detectGeoPositionUtils import detectGeoLocation
from src.utils.utils import *
from src.database.databaseUtils import insertHistory, createSecretCode

from src.database.SQLRequests import user as SQLUser
from src.database.SQLRequests import events as SQLEvents

from src import email_templates as emails

app = Blueprint('user', __name__)


def check_tg_auth_hash(id, first_name, last_name, username, photo_url, auth_date, hash):
    data_check_string = \
        (f"auth_date={auth_date}" if auth_date else "") + \
        (f"\nfirst_name={first_name}" if first_name else "") + \
        (f"\nid={id}" if id else "") + \
        (f"\nlast_name={last_name}" if last_name else "") + \
        (f"\nphoto_url={photo_url}" if photo_url else "") + \
        (f"\nusername={username}" if username else "")

    secret_key = hashlib.sha256(config["tg_bot_token"].encode('utf-8')).digest()
    expected_hash = hmac.new(secret_key, bytes(data_check_string, 'utf-8'), hashlib.sha256).hexdigest()

    authTime = datetime.datetime.fromtimestamp(auth_date)
    currentTime = datetime.datetime.now()
    return (
            (currentTime - authTime).total_seconds() < 60 * float(config["allow_auth_period_min"]) and
            expected_hash == hash
    )


def new_session(resp, browser, osName, geolocation, ip):
    token = str(uuid.uuid4())
    hoursAlive = 24 * 7  # 7 days
    session = DB.execute(SQLUser.insertSession, [resp['id'], token, hoursAlive, ip, browser, osName, geolocation])
    expires = session['expires']

    DB.execute(SQLUser.deleteExpiredSessions)

    res = jsonResponse(resp)
    res.set_cookie("session_token", token, expires=expires, httponly=True, samesite="lax")
    return res


def authOrRegisterUserByUserData(userData, tgId, tgUsername, tgUserLastname, tgUserFirstname, tgPhotourl, clientBrowser,
                                 clientOS):
    if not userData or not userData['tel']:  # No user or not full data
        if not userData:
            # Register new user
            try:
                userData = DB.execute(SQLUser.insertUser,
                                      [tgId, tgUsername, tgPhotourl, None, None, tgUserLastname, tgUserFirstname, None])
            except:
                return jsonResponse("Не удалось создать аккаунт без данных. Внутренняя ошибка", HTTP_INTERNAL_ERROR)
        # not full data

        insertHistory(
            userData['id'],
            'account',
            f'Create partial account: @{tgUsername} #{tgId}, {tgUserFirstname} {tgUserLastname}, avatarUrl={tgPhotourl}'
        )
        return new_session(userData, clientBrowser, clientOS, detectGeoLocation(), request.environ['IP_ADDRESS'])

    insertHistory(
        userData['id'],
        'account',
        'Login existing account'
    )

    # Update tg user data to actual
    if tgPhotourl is None:
        DB.execute(SQLUser.updateUserTgDataWithoutAvatarUrlById, [str(tgId), tgUsername, userData['id']])
    else:
        DB.execute(SQLUser.updateUserTgDataById, [str(tgId), tgUsername, tgPhotourl, userData['id']])

    return new_session(userData, clientBrowser, clientOS, detectGeoLocation(), request.environ['IP_ADDRESS'])


@app.route("/auth", methods=["POST"])
def userAuthOrRegister():
    try:
        req = request.json
        tgId = req['tgId']
        tgUsername = req.get('tgUsername')
        tgHash = req['tgHash']
        tgAuthDate = req['tgAuthDate']
        tgPhotoUrl = req.get('tgPhotoUrl')
        tgFirstName = req.get('tgFirstName')
        tgLastName = req.get('tgLastName')
        clientBrowser = req.get('clientBrowser') or 'Unknown browser'
        clientOS = req.get('clientOS') or 'Unknown OS'
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if not check_tg_auth_hash(tgId, tgFirstName, tgLastName, tgUsername, tgPhotoUrl, tgAuthDate, tgHash):
        return jsonResponse("Хэш авторизации TG не совпадает с данными", HTTP_INVALID_AUTH_DATA)

    resp = DB.execute(SQLUser.selectUserByTgUsernameOrTgId, [tgUsername, str(tgId)])
    return authOrRegisterUserByUserData(
        resp, tgId, tgUsername, tgLastName, tgFirstName, tgPhotoUrl,
        clientBrowser, clientOS
    )


@app.route("/auth/code", methods=["POST"])
def userAuthOrRegisterByCode():
    try:
        req = request.json
        secretCode = req['code']
        clientBrowser = req.get('clientBrowser') or 'Unknown browser'
        clientOS = req.get('clientOS') or 'Unknown OS'
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    resp = DB.execute(SQLUser.selectSecretCodeByCodeType, [secretCode, 'auth'])
    if not resp:
        return jsonResponse("Неверный одноразовый код", HTTP_INVALID_AUTH_DATA)
    DB.execute(SQLUser.deleteSecretCodeByUseridCode, [resp['userid'], resp['code']])

    tgUserData = json.loads(resp['meta'])

    resp = DB.execute(SQLUser.selectUserByTgUsernameOrTgId, [tgUserData['username'], str(tgUserData['id'])])
    return authOrRegisterUserByUserData(
        resp, tgUserData['id'], tgUserData['username'], tgUserData['last_name'], tgUserData['first_name'], None,
        clientBrowser, clientOS
    )


@app.route("/session", methods=["DELETE"])
@login_required
def userSessionDelete(userData):
    try:
        DB.execute(SQLUser.deleteSessionByToken, [userData['session_token']])
    except:
        return jsonResponse("Сессия не удалена", HTTP_INTERNAL_ERROR)

    res = jsonResponse("Вы вышли из аккаунта")
    res.set_cookie("session_token", "", max_age=-1, httponly=True, samesite="none", secure=True)

    insertHistory(
        userData['id'],
        'account',
        'Logout'
    )
    return res


@app.route("/sessions/another", methods=["DELETE"])
@login_required
def userAnotherSessionsDelete(userData):
    try:
        DB.execute(SQLUser.deleteAllUserSessionsWithoutCurrent, [userData['id'], userData['session_token']])
    except:
        return jsonResponse("Сессия не удалена", HTTP_INTERNAL_ERROR)

    res = jsonResponse("Вы вышли из аккаунта")
    return res


@app.route("/sessions/all")
@login_required
def getAllUserSessions(userData):
    try:
        sessions = DB.execute(SQLUser.selectAllUserSessions, [userData['id']], manyResults=True)
    except:
        return jsonResponse("Не удалось получить список сессий", HTTP_INTERNAL_ERROR)

    for session in sessions:
        times_to_str(session)
        if session['token'] == userData['session_token']:
            session['isCurrent'] = True
        else:
            session['isCurrent'] = False
        del session['token']
    return jsonResponse({'sessions': sessions})


@app.route("")
@login_or_none
def userGet(userData):
    try:
        req = request.args
        userId = req.get('id')
        tgId = req.get('tgId')
        tgUsername = req.get('tgUsername')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    def addEvents(userData):
        allEvents = DB.execute(SQLEvents.selectEvents({"registrationId": userData['id']}), manyResults=True)
        list_times_to_str(allEvents)
        resEvents = []
        for event in allEvents:
            resEvents.append({
                "id": event["id"],
                "title": event["title"],
            })
        userData['completedevents'] = resEvents

    if tgUsername is not None or tgId is not None:  # return user data by tgUsername or tgId
        user = DB.execute(SQLUser.selectUserIdByTgUsernameOrTgId, [tgUsername, str(tgId)])
        if not user:
            return jsonResponse("Пользователя с таким tgUsername или tgId не существует", HTTP_NOT_FOUND)
        return jsonResponse(user)

    if userId is None:  # return self user data
        if userData is None:
            return jsonResponse("Не авторизован", HTTP_INVALID_AUTH_DATA)
        addEvents(userData)
        return jsonResponse(userData)

    # get another user data
    if userData['caneditusersdata']:
        anotherUserData = DB.execute(SQLUser.selectUserById, [userId])
    else:
        anotherUserData = DB.execute(SQLUser.selectAnotherUserById, [userId])
    if not anotherUserData:
        return jsonResponse("Пользователь не найден", HTTP_NOT_FOUND)
    addEvents(anotherUserData)
    return jsonResponse(anotherUserData)


@app.route("", methods=["PUT"])
@login_required
def userUpdate(userData):
    try:
        req = request.json
        userId = req['id']
        givenName = req.get('givenName')
        familyName = req.get('familyName')
        middleName = req.get('middleName')
        email = req.get('email')
        avatarUrl = req.get('avatarUrl')
        tel = req.get('tel')

        level = req.get('level')
        tgUsername = req.get('tgUsername')
        tgId = req.get('tgId')
        canEditAchievements = req.get('canEditAchievements')
        canAssignAchievements = req.get('canAssignAchievements')
        canEditRegistrations = req.get('canEditRegistrations')
        canEditEvents = req.get('canEditEvents')
        canEditUsersData = req.get('canEditUsersData')
        canEditDocs = req.get('canEditDocs')
        canExecuteSQL = req.get('canExecuteSQL')
        canEditHistory = req.get('canEditHistory')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if str(userData['id']) != str(userId):
        if not userData['caneditusersdata']:
            return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)
        userData = DB.execute(SQLUser.selectUserById, [userId])

    if email: email = email.strip().lower()
    if givenName: givenName = givenName.strip()
    if familyName: familyName = familyName.strip()
    if middleName: middleName = middleName.strip()

    givenName = givenName or userData['givenname']
    familyName = familyName or userData['familyname']
    middleName = middleName or userData['middlename']
    email = email or userData['email']
    avatarUrl = avatarUrl or userData['avatarurl']
    tel = tel or userData['tel']
    level = level or userData['level']
    tgUsername = tgUsername or userData['tgusername']
    tgId = tgId or userData['tgid']
    canEditAchievements = canEditAchievements or userData['caneditachievements']
    canAssignAchievements = canAssignAchievements or userData['canassignachievements']
    canEditRegistrations = canEditRegistrations or userData['caneditregistrations']
    canEditEvents = canEditEvents or userData['caneditevents']
    canEditUsersData = canEditUsersData or userData['caneditusersdata']
    canEditDocs = canEditDocs or userData['caneditdocs']
    canExecuteSQL = canExecuteSQL or userData['canexecutesql']
    canEditHistory = canEditHistory or userData['canedithistory']

    try:
        if userData['caneditusersdata']:
            resp = DB.execute(SQLUser.adminUpdateUserById,
                              [givenName, familyName, middleName, email, tel, avatarUrl, level, tgUsername,
                               tgId, canEditAchievements, canAssignAchievements, canEditRegistrations, canEditEvents,
                               canEditUsersData, canEditDocs, canExecuteSQL, canEditHistory, userId])
        else:
            resp = DB.execute(SQLUser.updateUserById,
                              [givenName, familyName, middleName, email, tel, avatarUrl, userId])
    except:
        return jsonResponse("Имя пользователя или email заняты", HTTP_DATA_CONFLICT)

    insertHistory(
        userId,
        'account',
        f'Update by user #{userData["id"]}: {json.dumps(req)}'
    )
    return jsonResponse(resp)


@app.route("", methods=["DELETE"])
@login_required
def userDelete(userData):
    try:
        req = request.json
        userId = req['userId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if (str(userData['id']) != str(userId)) and (not userData['caneditusersdata']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    DB.execute(SQLUser.deleteUserById, [userId])

    insertHistory(
        userId,
        'account',
        f'Delete by user #{userData["id"]}'
    )
    return jsonResponse("Пользователь удален")


@app.route("/all")
def usersGetAll():
    try:
        req = request.args
        search = req.get('search')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    resp = DB.execute(SQLUser.selectUsersByFilters(req), manyResults=True)
    return jsonResponse({'users': resp})


@app.route("/email/confirmation/send", methods=["POST"])
@login_required
def userConfirmEmailSendMessage(userData):
    email = userData['email']

    userData = DB.execute(SQLUser.selectUserByEmail, [email])
    if not userData:
        return jsonResponse("На этот email не зарегистрирован ни один аккаунт", HTTP_NOT_FOUND)

    secretCode = createSecretCode(userData['id'], "email", hours=24)

    send_email(email,
               f"Подтверждение регистрации на {config['project_name']}",
               emails.confirmEmail(userData['avatarurl'], userData['givenname'] + ' ' + userData['familyname'], secretCode))

    insertHistory(
        userData['id'],
        'account',
        f'Email for confirmation sent'
    )
    return jsonResponse("Ссылка для подтверждения email выслана на почту " + email)


@app.route("/email/confirmation", methods=["POST"])
def userConfirmEmail():
    try:
        req = request.json
        code = req['code']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    resp = DB.execute(SQLUser.updateUserConfirmationBySecretcodeType, [code, "email"])
    if not resp:
        return jsonResponse("Неверный одноразовый код", HTTP_INVALID_AUTH_DATA)

    DB.execute(SQLUser.deleteSecretCodeByCodeType, [code, "email"])

    insertHistory(
        resp['id'],
        'account',
        f'Email confirmed'
    )
    return jsonResponse("Адрес email подтвержден")
