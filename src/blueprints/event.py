from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *
from src.database.databaseUtils import insertHistory

from src.database.SQLRequests import events as SQLEvents

app = Blueprint('events', __name__)


@app.route("")
@login_required
def eventsGet(userData):
    try:
        req = request.args
        id = req.get('id')

        dateStart = req.get('dateStart')
        dateEnd = req.get('dateEnd')
        search = req.get('search')
        registrationId = req.get('registrationId')
        type = req.get('type')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    if id is not None:  # get single event
        eventData = DB.execute(SQLEvents.selectEventById, [id])
        times_to_str(eventData)
        registrations = DB.execute(SQLEvents.selectRegistrationsByEventid, [eventData['id']], manyResults=True)
        eventData['registrationscount'] = len(registrations)
        if userData['caneditevents']:
            eventData['registrations'] = registrations
        res = DB.execute(SQLEvents.selectRegistrationByUseridEventid, [userData['id'], id])
        eventData['isyouregistered'] = bool(res)
        eventData['isyourregistrationconfirmed'] = res['isconfirmed'] if res else None
        eventData['yourcomment'] = res['usercomment'] if res else None
        return jsonResponse(eventData)

    # get events list by filters
    events = DB.execute(SQLEvents.selectEvents(req), [], manyResults=True)
    list_times_to_str(events)
    for event in events:
        countRes = DB.execute(SQLEvents.selectRegistrationsCountByEventid, [event['id']])
        event['registrationscount'] = countRes.get('count') or 0
        res = DB.execute(SQLEvents.selectRegistrationByUseridEventid, [userData['id'], event['id']])
        event['isyouregistered'] = bool(res)
        event['isyourregistrationconfirmed'] = res['isconfirmed'] if res else None
        event['yourcomment'] = res['usercomment'] if res else None
    return jsonResponse({"events": events})


@app.route("", methods=["POST"])
@login_and_can_edit_events_required
def eventCreate(userData):
    try:
        req = request.json
        title = req['title']
        description = req.get('description')
        routeDescription = req.get('routeDescription')
        startDate = req['startDate']
        cameDate = req['cameDate']
        previewUrl = req.get('previewUrl')
        customCSS = req.get('customCSS')
        lapDistanceKm = req.get('lapDistanceKm')
        medalPreviewUrl = req.get('medalPreviewUrl')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    event = DB.execute(SQLEvents.insertEvent, [title, description, routeDescription, previewUrl, customCSS, lapDistanceKm, medalPreviewUrl, userData['id'], startDate, cameDate])
    times_to_str(event)

    insertHistory(
        userData["id"],
        'events',
        f'Creates event: "{event["title"]}" #{event["id"]}'
    )

    return jsonResponse(event)


@app.route("", methods=["PUT"])
@login_and_can_edit_events_required
def eventUpdate(userData):
    try:
        req = request.json
        id = req['id']
        title = req['title']
        description = req.get('description')
        routeDescription = req.get('routeDescription')
        startDate = req['startDate']
        cameDate = req['cameDate']
        previewUrl = req.get('previewUrl')
        customCSS = req.get('customCSS')
        lapDistanceKm = req.get('lapDistanceKm')
        medalPreviewUrl = req.get('medalPreviewUrl')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    eventData = DB.execute(SQLEvents.selectEventById, [id])
    if eventData is None:
        return jsonResponse("Событие не найдено", HTTP_NOT_FOUND)
    times_to_str(eventData)

    if title is None: name = eventData['name']
    if description is None: description = eventData['description']
    if routeDescription is None: routeDescription = eventData['routedescription']
    if startDate is None: startDate = eventData['startdate']
    if cameDate is None: cameDate = eventData['camedate']
    if previewUrl is None: previewUrl = eventData['previewurl']
    if customCSS is None: customCSS = eventData['customcss']
    if lapDistanceKm is None: lapDistanceKm = eventData['lapdistancekm']
    if medalPreviewUrl is None: medalPreviewUrl = eventData['medalpreviewurl']

    event = DB.execute(SQLEvents.updateEventById, [title, description, routeDescription, startDate, cameDate, previewUrl, customCSS, lapDistanceKm, medalPreviewUrl, id])
    times_to_str(event)

    insertHistory(
        userData["id"],
        'events',
        f'Updates event: {json.dumps(req)}'
    )

    return jsonResponse(event)


@app.route("", methods=["DELETE"])
@login_and_can_edit_events_required
def eventDelete(userData):
    try:
        req = request.json
        id = req['id']
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    DB.execute(SQLEvents.deleteEventById, [id])

    insertHistory(
        userData["id"],
        'events',
        f'Deletes event: #{id}'
    )

    return jsonResponse("Событие удалено")
