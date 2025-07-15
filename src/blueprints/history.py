from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *

from src.database.SQLRequests import history as SQLHistory

app = Blueprint('history', __name__)

@app.route("")
def history():
    try:
        req = request.args

        userId = req.get('userId')
        search = req.get('search')
        type = req.get('type')
        dateStart = req.get('dateStart')
        dateEnd = req.get('dateEnd')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    # get history list by filters
    history = DB.execute(SQLHistory.selectHistory(req), [], manyResults=True)
    return jsonResponse({"history": history})
