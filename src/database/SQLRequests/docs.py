import json

insertDoc = \
    "INSERT INTO docs (title, text, authorId, lastRedactorId) " \
    "VALUES (%s, %s, %s, %s) " \
    "RETURNING *"

# ------------------

def selectDocs(filters):
    order = json.loads(filters.get('order')) if filters.get('order') else []
    search = filters.get('search', '').lower()

    return \
            f"SELECT docs.*, (users.givenName  || ' ' || users.familyName) as authorname, users.tgusername authortelegram, (ured.givenName  || ' ' || ured.familyName) lastredactorname, ured.tgusername lastredactortelegram FROM docs " \
            "LEFT JOIN users ON docs.authorId = users.id " + \
            "LEFT JOIN users ured ON docs.lastRedactorId = ured.id " + \
            "WHERE " + \
            (f"LOWER(title) LIKE '%%{search}%%' AND " if 'search' in filters else "") + \
            "1 = 1 " \
            "ORDER BY " + f"{', '.join(order + ['id'])}"

selectDocById = \
    "SELECT docs.*, (users.givenName  || ' ' || users.familyName) as authorname, users.tgusername authortelegram, (ured.givenName  || ' ' || ured.familyName) lastredactorname, ured.tgusername lastredactortelegram FROM docs " \
    "LEFT JOIN users ON docs.authorId = users.id " \
    "WHERE docs.id = %s"

# ------------------

updateDocById = \
    "UPDATE docs SET " \
    "title = %s, " \
    "text = %s, " \
    "lastredactorid = %s " \
    "WHERE id = %s " \
    "RETURNING *"

# ------------------

deleteDocById = \
    "DELETE FROM docs " \
    "WHERE id = %s "
