insertDoc = \
    "INSERT INTO docs (title, text, authorId, lastRedactorId) " \
    "VALUES (%s, %s, %s, %s) " \
    "RETURNING *"

# ------------------

def selectDocs(filters):
    return \
            f"SELECT docs.*, (users.givenName  || ' ' || users.familyName) as authorname, users.tgusername authortelegram, (ured.givenName  || ' ' || ured.familyName) lastredactorname, ured.tgusername lastredactortelegram FROM docs " \
            "LEFT JOIN users ON docs.authorId = users.id " + \
            "LEFT JOIN users ured ON docs.lastRedactorId = ured.id " + \
            "WHERE " + \
            (f"LOWER(title) LIKE '%%{filters['search'].lower()}%%' AND " if 'search' in filters else "") + \
            "1 = 1 " \
            "ORDER BY title"

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
