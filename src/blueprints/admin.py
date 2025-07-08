from flask import Blueprint

from src.utils.access import *
from src.constants import *
from src.utils.utils import *

from src.database.SQLRequests import events as SQLEvents

app = Blueprint('admin', __name__)


@app.route("/sql", methods=["POST"])
@login_and_can_execute_sql_required
def executeSQL(userData):
    try:
        req = request.json
        sqlText = req['sql']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    try:
        resp = DB.execute(sqlText, manyResults=True)
        list_times_to_str(resp)
        return jsonResponse({"response": resp})
    except Exception as err:
        return jsonResponse(str(err), HTTP_INTERNAL_ERROR)


@app.route("/registration/confirmation", methods=["PUT"])
@login_and_can_edit_registrations_required
def setToUserAdminConfirmation(userData):
    try:
        req = request.json
        registrationId = req['registrationId']
        isConfirmed = req['isConfirmed']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    resp = DB.execute(SQLEvents.updateRegistrationById, [isConfirmed, userId], manyResults=True)
    return jsonResponse(resp)
