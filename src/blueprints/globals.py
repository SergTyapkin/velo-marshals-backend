import json

from flask import Blueprint

from src.utils.access import *
from src.constants import *
from src.utils.utils import *
from src.database.databaseUtils import insertHistory

from src.database.SQLRequests import globals as SQLGlobals

app = Blueprint('globals', __name__)


@app.route("", methods=["PUT"])
@login_and_can_edit_globals_required
def globalsUpdate(userData):
    try:
        req = request.json
        inEventId = req.get('inEventId')
        isOnMaintenance = req.get('isOnMaintenance')
    except Exception as err:
        return jsonResponse(f"Не удалось сериализовать json: {err.__repr__()}", HTTP_INVALID_DATA)

    globalsData = DB.execute(SQLGlobals.selectGlobals)

    if inEventId is None:
        inEventId = globalsData['ineventid']
    elif int(inEventId) < 0:
        inEventId = None
    isOnMaintenance = isOnMaintenance if isOnMaintenance is not None else globalsData['isonmaintenance']

    resp = DB.execute(SQLGlobals.updateGlobals, [inEventId, isOnMaintenance])

    insertHistory(
        userData['id'],
        'globals',
        f'Set globals: {json.dumps(req)}'
    )
    return jsonResponse(resp)

