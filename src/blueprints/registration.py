from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *
from src.database.databaseUtils import insertHistory

from src.database.SQLRequests import events as SQLEvents

app = Blueprint('registrations', __name__)


@app.route("/unconfirmed", methods=["GET"])
@login_and_can_edit_registrations_required
def getUnvotedRegistrations(userData):
    try:
        req = request.json
        eventId = req['eventId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    resp = DB.execute(SQLEvents.selectRegistrationsUnconfirmedByEventid, [eventId], manyResults=True)
    list_times_to_str(resp)
    return jsonResponse({'registrations': resp})


@app.route("/event", methods=["GET"])
@login_required
def getRegistrationsByEvent(userData):
    try:
        req = request.json
        eventId = req['eventId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    resp = DB.execute(SQLEvents.selectRegistrationsByEventid, [eventId], manyResults=True)
    if resp is None:
        return jsonResponse("Событие не найдено", HTTP_NOT_FOUND)

    return jsonResponse(resp)


@app.route("/event", methods=["POST"])
@login_required
def registerToEvent(userData):
    try:
        req = request.json
        eventId = req['eventId']
        userId = req['userId']
        userComment = req.get('userComment')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if (str(userId) != str(userData['id'])) and (not userData['caneditregistrations']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    eventData = DB.execute(SQLEvents.selectEventById, [eventId])
    if eventData is None:
        return jsonResponse("Такого события не существует", HTTP_NOT_FOUND)

    if (not eventData['isinfuture']) and (not userData['caneditregistrations']):
        return jsonResponse("Событие уже закончилось, а вы - не админ", HTTP_DATA_CONFLICT)

    try:
        response = DB.execute(SQLEvents.insertRegistration, [eventId, userId, userComment])
    except:
        return jsonResponse("Пользователь уже записан на это мероприятие", HTTP_DATA_CONFLICT)

    insertHistory(
        userId,
        'registration',
        f'Add registration on event: "{eventData["title"]}" #{eventId}'
    )

    return jsonResponse(response)


@app.route("/event", methods=["DELETE"])
@login_required
def unregisterToEvent(userData):
    try:
        req = request.json
        eventId = req['eventId']
        userId = req['userId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if (str(userId) != str(userData['id'])) and (not userData['caneditregistrations']):
        return jsonResponse("Недостаточно прав доступа", HTTP_NO_PERMISSIONS)

    eventData = DB.execute(SQLEvents.selectEventById, [eventId])
    if not eventData:
        return jsonResponse("Такого события не существует", HTTP_NOT_FOUND)

    if (not eventData['isinfuture']) and (not userData['caneditregistrations']):
        return jsonResponse("Событие уже закончилось, а вы - не админ", HTTP_DATA_CONFLICT)

    DB.execute(SQLEvents.deleteRegistrationByEventidUserid, [eventId, userId])

    insertHistory(
        userId,
        'registration',
        f'Delete registration from event: "{eventData["title"]}" #{eventId}'
    )

    return jsonResponse("Запись на событие удалена")


@app.route("/event", methods=["PUT"])
@login_and_can_edit_registrations_required
def updateRegistrationData(userData):
    try:
        req = request.json
        id = req['id']
        isConfirmed = req.get('isConfirmed')
        adminComment = req.get('adminComment')
        level = req.get('level')
        salary = req.get('salary')
        taskText = req.get('taskText')
        lapsPassed = req.get('lapsPassed')
        cameDate = req.get('leaveDate')
        leaveDate = req.get('leaveDate')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    registrationData = DB.execute(SQLEvents.selectRegistrationById, [id])
    if registrationData is None:
        return jsonResponse("Такой регистрации не существует", HTTP_NOT_FOUND)

    if isConfirmed is None and 'isConfirmed' not in req: isConfirmed = registrationData['isconfirmed']
    if adminComment is None: adminComment = registrationData['admincomment']
    if level is None: level = registrationData['level']
    if salary is None: salary = registrationData['salary']
    if taskText is None: taskText = registrationData['tasktext']
    if lapsPassed is None: lapsPassed = registrationData['lapspassed']
    if cameDate is None: cameDate = registrationData['camedate']
    if leaveDate is None: leaveDate = registrationData['leavedate']

    response = DB.execute(SQLEvents.updateRegistrationById,
                          [isConfirmed, adminComment, level, salary, taskText, lapsPassed, cameDate, leaveDate, id])

    insertHistory(
        registrationData['userid'],
        'registration',
        f'Batch update registration: {json.dumps(req)}'
    )

    return jsonResponse(response)


@app.route("/event/comment", methods=["PUT"])
@login_required
def updateSelfRegistrationComment(userData):
    try:
        req = request.json
        id = req['id']
        userComment = req['userComment']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    registrationData = DB.execute(SQLEvents.selectRegistrationById, [id])
    if registrationData is None:
        return jsonResponse("Такой регистрации не существует", HTTP_NOT_FOUND)
    if registrationData['userid'] != userData['id'] and not userData['caneditregistrations']:
        return jsonResponse("Нет прав на редактирование чужого комментария", HTTP_NO_PERMISSIONS)

    insertHistory(
        registrationData['userid'],
        'registration',
        f'Update comment: {registrationData["usercomment"]}'
    )

    response = DB.execute(SQLEvents.updateRegistrationUserCommentById, [userComment, id])
    return jsonResponse(response)


@app.route("/camedate", methods=["PUT"])
@login_and_can_edit_registrations_required
def updateCameDate(userData):
    try:
        req = request.json
        id = req['id']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    registrationData = DB.execute(SQLEvents.updateRegistrationCameDateById, [id])
    if registrationData is None:
        return jsonResponse("Такой регистрации не существует", HTTP_NOT_FOUND)

    insertHistory(
        registrationData['userid'],
        'registration',
        f'Set came date: {registrationData["camedate"]}'
    )

    return jsonResponse(registrationData)


@app.route("/leavedate", methods=["PUT"])
@login_and_can_edit_registrations_required
def updateLeaveDate(userData):
    try:
        req = request.json
        id = req['id']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    registrationData = DB.execute(SQLEvents.updateRegistrationLeaveDateById, [id])
    if registrationData is None:
        return jsonResponse("Такой регистрации не существует", HTTP_NOT_FOUND)

    insertHistory(
        registrationData['userid'],
        'registration',
        f'Set leave date: {registrationData["leavedate"]}'
    )

    return jsonResponse(registrationData)


@app.route("/lap-increase", methods=["PUT"])
@login_and_can_edit_registrations_required
def updateIncreaseLapsPassed(userData):
    try:
        req = request.json
        id = req['id']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    registrationData = DB.execute(SQLEvents.updateIncreaseRegistrationLapsPassedById, [id])
    if registrationData is None:
        return jsonResponse("Такой регистрации не сущеcтвует", HTTP_NOT_FOUND)

    insertHistory(
        registrationData['userid'],
        'registration',
        f'Increase lap by 1. Number of laps: {registrationData["lapspassed"]}'
    )

    return jsonResponse(registrationData)
