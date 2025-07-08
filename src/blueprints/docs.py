from flask import Blueprint

from src.utils.access import *
from src.utils.utils import *

from src.database.SQLRequests import docs as SQLDocs


app = Blueprint('docs', __name__)


@app.route("")
@login_required_return_id
def docsGet(userId):
    try:
        req = request.args
        id = req.get('id')

        search = req.get('search')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    if id is not None:  # get single doc
        docData = DB.execute(SQLDocs.selectDocById, [id])
        if docData is None:
            return jsonResponse("Документ не найден", HTTP_NOT_FOUND)
        return jsonResponse(docData)

    # get docs list by filters
    docs = DB.execute(SQLDocs.selectDocs(req), [], manyResults=True)
    return jsonResponse({"docs": docs})


@app.route("", methods=["POST"])
@login_and_can_edit_docs_required
def docCreate(userData):
    try:
        req = request.json
        title = req['title']
        text = req['text']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    doc = DB.execute(SQLDocs.insertDoc, [title, text, userData['id'], userData['id']])

    return jsonResponse(doc)


@app.route("", methods=["PUT"])
@login_and_can_edit_docs_required
def docUpdate(userData):
    try:
        req = request.json
        id = req['id']
        title = req.get('title')
        text = req.get('text')
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    docData = DB.execute(SQLDocs.selectDocById, [id])
    if docData is None:
        return jsonResponse("Документ не найден", HTTP_NOT_FOUND)

    if title is None: title = docData['title']
    if text is None: text = docData['text']

    doc = DB.execute(SQLDocs.updateDocById, [title, text, userData['id'], id])

    return jsonResponse(doc)


@app.route("", methods=["DELETE"])
@login_and_can_edit_docs_required
def docDelete(userData):
    try:
        req = request.json
        id = req['id']
    except:
        return jsonResponse("Не удалось сериализовать json", HTTP_INVALID_DATA)

    DB.execute(SQLDocs.deleteDocById, [id])
    return jsonResponse("Документ удален")
