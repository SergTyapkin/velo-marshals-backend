from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *
from src.database.databaseUtils import insertHistory

from src.database.SQLRequests import equipment as SQLEquipment

app = Blueprint('equipment', __name__)


@app.route("")
@login_required_return_id
def equipmentGetSingle(userId):
    try:
        req = request.args
        id = req['id']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectEquipmentById, [id])
    if not equipment:
        return jsonResponse("Такого оборудования не найдено", HTTP_NOT_FOUND)
    return jsonResponse(equipment)


@app.route("/event/groups")
@login_required_return_id
def equipmentGroupsGet(userId):
    try:
        req = request.args
        eventId = req['eventId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectEquipmentsGroupsByEventId, [eventId], manyResults=True)
    return jsonResponse({"equipmentGroups": equipment})

@app.route("/event")
@login_required_return_id
def equipmentGet(userId):
    try:
        req = request.args
        eventId = req['eventId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectEquipmentsByEventId, [eventId], manyResults=True)
    return jsonResponse({"equipment": equipment})


@app.route("/event", methods=["POST"])
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
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

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
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

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
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    DB.execute(SQLEquipment.deleteEquipmentById, [id])

    insertHistory(
        userData["id"],
        'equipment',
        f'Deletes equipment: #{id}'
    )

    return jsonResponse("Оборудование удалено")


@app.route("/take", methods=["POST"])
@login_required_return_id
def equipmentTakeFromAnother(userId):
    try:
        req = request.json
        id = req['id']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectEquipmentById, [id])
    if not equipment:
        return jsonResponse("Не известное id оборудования", HTTP_NOT_FOUND)

    DB.execute(SQLEquipment.deleteUserEquipmentByEquipmentId, [id])
    DB.execute(SQLEquipment.insertUserEquipment, [userId, id, equipment['amounttotal']])

    insertHistory(
        userId,
        'equipment',
        f'Take equipment from another user. Equipment: #{id} {equipment["title"]}'
    )

    return jsonResponse("Оборудование записано")


@app.route("/event/holders", methods=["GET"])
@login_required
def equipmentHoldersGet(userData):
    try:
        req = request.args
        eventId = req['eventId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectEquipmentUsersHoldersByEquipmentIdEventId, [eventId], manyResults=True)

    return jsonResponse({"holders": equipment})


@app.route("/event/holder", methods=["GET"])
@login_required
def equipmentHoldersDelete(userData):
    try:
        req = request.args
        userId = req['userId']
        eventId = req['eventId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    equipment = DB.execute(SQLEquipment.selectUserEquipmentsByUseridEquipmentId, [userId, eventId], manyResults=True)

    return jsonResponse({"equipment": equipment})


@app.route("/event/holders/history", methods=["GET"])
@login_and_can_edit_events_required
def equipmentHoldersHistoryGet(userData):
    try:
        req = request.args
        eventId = req['eventId']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    history = DB.execute(SQLEquipment.selectEquipmentsHistoryByEventId, [eventId], manyResults=True)

    return jsonResponse({"history": history})


@app.route("/holder/add", methods=["PUT"])
@login_required
def addEquipmentToUser(userData):
    try:
        req = request.json
        userId = req['userId']
        equipmentId = req['equipmentId']
        amountAdd = int(req['amountAdd'])
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if userId != userData['id'] and not userData['caneditevents']:
        return jsonResponse("Нет прав доступа на запись оборудования на другого пользователя", HTTP_NOT_FOUND)

    equipment = DB.execute(SQLEquipment.selectEquipmentWithAmountLeftById, [equipmentId])
    if not equipment:
        return jsonResponse("Оборудование с таким id не найдено", HTTP_NOT_FOUND)
    if amountAdd > equipment['amountleft']:
        return jsonResponse("Нельзя записать больше, чем осталось", HTTP_DATA_CONFLICT)

    equipment = DB.execute(SQLEquipment.selectUserEquipmentsByUseridEquipmentId, [userId, equipmentId])
    if not equipment:
        equipment = DB.execute(SQLEquipment.insertUserEquipment, [userId, equipmentId, amountAdd])
    else:
        equipment = DB.execute(SQLEquipment.updateUserEquipmentAmountHoldsByUseridEquipmentId, [equipment['amountholds'] + amountAdd, userId, equipmentId])

    insertHistory(
        userId,
        'equipment',
        f'Adds equipment on user by #{userData["id"]}, equipment: #{equipment["id"]}, amount: {amountAdd}'
    )

    return jsonResponse(equipment)


@app.route("/holder/remove", methods=["PUT"])
@login_required
def removeEquipmentFromUser(userData):
    try:
        req = request.json
        userId = req['userId']
        equipmentId = req['equipmentId']
        amountRemove = int(req['amountRemove'])
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if userId != userData['id'] and not userData['caneditevents']:
        return jsonResponse("Нет прав доступа на запись оборудования на другого пользователя", HTTP_NOT_FOUND)

    equipment = DB.execute(SQLEquipment.selectUserEquipmentsByUseridEquipmentId, [userId, equipmentId])
    if not equipment:
        return jsonResponse("Пользователь не брал это оборудование", HTTP_DATA_CONFLICT)
    if amountRemove > equipment['amountholds']:
        return jsonResponse("Нельзя списать с пользователя больше оборудования, чем у него есть", HTTP_DATA_CONFLICT)
    if amountRemove == equipment['amountholds']:
        equipment = DB.execute(SQLEquipment.deleteUserEquipmentByUseridEquipmentId, [userId, equipmentId])
    else:
        equipment = DB.execute(SQLEquipment.updateUserEquipmentAmountHoldsByUseridEquipmentId, [equipment['amountholds'] - amountRemove, userId, equipmentId])

    insertHistory(
        userId,
        'equipment',
        f'Remove equipment from user by #{userData["id"]}, equipment: #{equipment["id"]}, amount: {amountRemove}'
    )

    return jsonResponse(equipment)
