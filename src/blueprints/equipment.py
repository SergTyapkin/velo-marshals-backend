import json

from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *

from src.database.SQLRequests import equipment as SQLEquipment

app = Blueprint('equipment', __name__)


@app.route("")
@login_required_return_id
def equipmentGet(userId):
    try:
        req = request.args
        eventId = req['eventId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectEquipmentsByEventId, [eventId], manyResults=True)
    return jsonResponse({"equipment": equipment})


@app.route("", methods=["POST"])
@login_and_can_edit_events_required
def equipmentCreate(userData):
    try:
        req = request.json
        title = req['title']
        eventId = req['eventId']
        description = req.get('description')
        previewUrl = req.get('previewUrl')
        amountTotal = req.get('amountTotal')
        isNeedsToReturn = req.get('isNeedsToReturn')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.insertEquipment,
                           [title, description, previewUrl, amountTotal, isNeedsToReturn, eventId])

    insertHistory(
        userData["id"],
        'equipment',
        f'Add equipment: "{equipment["title"]}" #{equipment["id"]}'
    )

    return jsonResponse(equipment)


@app.route("", methods=["PUT"])
@login_and_can_edit_events_required
def equipmentUpdate(userData):
    try:
        req = request.json
        id = req['id']
        title = req.get('title')
        description = req.get('description')
        previewUrl = req.get('previewUrl')
        amountTotal = req.get('amountTotal')
        isNeedsToReturn = req.get('isNeedsToReturn')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    equipmentData = DB.execute(SQLEquipment.selectEquipmentById, [id])
    if equipmentData is None:
        return jsonResponse("Оборудование не найдено", HTTP_NOT_FOUND)

    if title is None: title = equipmentData['title']
    if description is None: description = equipmentData['description']
    if previewUrl is None: previewUrl = equipmentData['previewurl']
    if amountTotal is None: amountTotal = equipmentData['amounttotal']
    if isNeedsToReturn is None: isNeedsToReturn = equipmentData['isneedstoreturn']

    equipment = DB.execute(SQLEquipment.updateEquipmentById,
                           [title, description, previewUrl, amountTotal, isNeedsToReturn, id])

    insertHistory(
        userData["id"],
        'equipment',
        f'Updates equipment: {json.dumps(req)}'
    )

    return jsonResponse(equipment)


@app.route("", methods=["DELETE"])
@login_and_can_edit_events_required
def equipmentDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(SQLEquipment.deleteEquipmentById, [id])

    insertHistory(
        userData["id"],
        'equipment',
        f'Deletes equipment: #{id}'
    )

    return jsonResponse("Оборудование удалено")


@app.route("/holders", methods=["GET"])
@login_required
def equipmentDelete(userData):
    try:
        req = request.json
        eventId = req['eventId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectEquipmentUsersHoldersByEquipmentIdEventId, [eventId], manyResults=True)

    return jsonResponse({"holders": equipment})


@app.route("/holder", methods=["GET"])
@login_and_can_edit_events_required
def equipmentDelete(userData):
    try:
        req = request.json
        userId = req['userId']
        eventId = req['eventId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectUserEquipmentsByUseridEventId, [userId, eventId])

    return jsonResponse(equipment)


@app.route("/holders/history", methods=["GET"])
@login_and_can_edit_events_required
def equipmentDelete(userData):
    try:
        req = request.json
        eventId = req['eventId']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    history = DB.execute(SQLEquipment.selectEquipmentsHistoryByEventId, [eventId], manyResults=True)

    return jsonResponse({"history": history})


@app.route("/holder", methods=["POST"])
@login_required
def equipmentDelete(userData):
    try:
        req = request.json
        userId = req['userId']
        equipmentId = req['equipmentId']
        amountHolds = req['amountHolds']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if userId != userData['userId'] and not userData['caneditevents']:
        return jsonResponse("Нет прав доступа на запись оборудования на другого пользователя", HTTP_NOT_FOUND)
    equipment = DB.execute(SQLEquipment.insertUserEquipment, [userId, equipmentId, amountHolds])

    insertHistory(
        userId,
        'equipment',
        f'Sets equipment on user by #{userData["id"]}, equipment: #{equipment["id"]}, amount: {amountHolds}'
    )

    return jsonResponse(equipment)


@app.route("/holder", methods=["PUT"])
@login_and_can_edit_events_required
def equipmentDelete(userData):
    try:
        req = request.json
        id = req['id']
        amount = req['amount']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.updateUserEquipmentAmountHoldsById, [amount, id])

    insertHistory(
        equipment['userid'],
        'equipment',
        f'Sets equipment amount by #{userData["id"]}: "{equipment["title"]}", #{equipment["id"]}, amount: {amount}'
    )

    return jsonResponse(equipment)


@app.route("/holder", methods=["DELETE"])
@login_and_can_edit_events_required
def equipmentDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(SQLEquipment.deleteUserEquipmentById, [id])

    insertHistory(
        userData["id"],
        'equipment',
        f'Deleted equipment on user: #{id}'
    )

    return jsonResponse("Оборудование списано с пользователя")
