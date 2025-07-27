insertEvent = \
    "INSERT INTO events (title, description, routeDescription, previewUrl, customCSS, lapDistanceKm, medalPreviewUrl, authorId, startDate, cameDate) " \
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) " \
    "RETURNING *"

insertRegistration = \
    "INSERT INTO registrations (eventId, userId, userComment) " \
    "VALUES (%s, %s, %s) " \
    "RETURNING *"

# ------------------

def selectEvents(filters):
    type = filters.get('type')
    dateStart = filters.get('dateStart')
    dateEnd = filters.get('dateEnd')
    search = filters.get('search')

    typeStr = "1 = 1 "
    if type == 'future':
        typeStr = "cameDate > NOW() "
    elif type == 'past':
        typeStr = "cameDate <= NOW() "

    registrationJoin = ""
    registrationWhere = ""
    if 'userId' in filters:
        registrationJoin = "JOIN registrations r ON r.eventId = events.id "
        registrationWhere = f"r.userId = {filters['userId']} AND "

    return \
            f"SELECT events.*, (users.givenName  || ' ' || users.familyName) as authorname, (events.cameDate >= NOW()) isinfuture FROM events " \
            "LEFT JOIN users ON events.authorId = users.id " + \
            registrationJoin + \
            "WHERE " + \
            (f"cameDate >= '{dateStart}' AND " if dateStart is not None else "") + \
            (f"cameDate < '{dateEnd}' AND " if dateEnd is not None else "") + \
            (f"LOWER(events.title) LIKE '%%{search.lower()}%%' AND " if search is not None else "") + \
            registrationWhere + typeStr + \
            "ORDER BY events.cameDate"

selectEventById = \
    "SELECT events.*, (users.givenName  || ' ' || users.familyName) as authorname, users.tgusername authortelegram, (events.cameDate >= NOW()) isinfuture FROM events " \
    "LEFT JOIN users ON events.authorId = users.id " \
    "WHERE events.id = %s"


selectRegistrationById = \
    "SELECT * FROM registrations " \
    "WHERE id = %s"

selectRegistrationByUseridEventid = \
    "SELECT * FROM registrations " \
    "WHERE userid = %s AND " \
    "eventid = %s"

selectRegistrationsByEventid = \
    "SELECT registrations.*, (users.givenName  || ' ' || users.familyName) as username, users.avatarUrl useravatarurl, users.tel usertel, users.tgUsername usertgusername FROM registrations " \
    "JOIN users ON registrations.userid = users.id " \
    "WHERE eventid = %s "

selectRegistrationsUnconfirmedByEventid = \
    "SELECT registrations.*, (users.givenName  || ' ' || users.familyName) as username, users.avatarUrl useravatarurl, users.tel usertel, users.tgUsername usertgusername FROM registrations " \
    "JOIN users ON registrations.userid = users.id " \
    "WHERE eventid = %s "

selectRegistrationsByUserId = \
    "SELECT registrations.*, (users.givenName  || ' ' || users.familyName) as username, users.avatarUrl useravatarurl, users.tel usertel, users.tgUsername usertgusername, events.medalPreviewUrl as eventmedalpreviewurl, events.id as eventid, events.title as eventtitle FROM registrations " \
    "JOIN users ON registrations.userid = users.id " \
    "JOIN events on registrations.eventid = events.id " \
    "WHERE userid = %s " \
    "ORDER BY events.cameDate"

selectRegistrationsCountByEventid = \
    "SELECT COUNT(*) count FROM registrations " \
    "WHERE eventid = %s"

def selectRatings(dateStart=None, dateEnd=None):
    return \
            "SELECT count(*) as rating, users.id, (users.givenName  || ' ' || users.familyName) as name, users.avatarUrl " \
            "FROM users " \
            "LEFT JOIN registrations ON registrations.userId = users.id " + \
            (f"LEFT JOIN events ON registrations.eventid = events.id " if dateStart is not None or dateEnd is not None else "") + \
            "WHERE " + \
            (f"events.date >= '{dateStart}' " if dateStart is not None else "") + \
            (f"AND events.date < '{dateEnd}' " if dateEnd is not None else "") + \
            "GROUP BY users.id " \
            "ORDER BY rating DESC"

# ------------------
updateEventById = \
    "UPDATE events SET " \
    "title = %s, " \
    "description = %s, " \
    "routeDescription = %s, " \
    "startDate = %s, " \
    "cameDate = %s, " \
    "previewUrl = %s, " \
    "customCSS = %s, " \
    "lapDistanceKm = %s, " \
    "medalPreviewUrl = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateRegistrationUserCommentById = \
    "UPDATE registrations SET " \
    "userComment = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateRegistrationCameDateById = \
    "UPDATE registrations SET " \
    "cameDate = NOW() " \
    "WHERE id = %s " \
    "RETURNING *"

updateRegistrationLeaveDateById = \
    "UPDATE registrations SET " \
    "leaveDate = NOW() " \
    "WHERE id = %s " \
    "RETURNING *"

updateIncreaseRegistrationLapsPassedById = \
    "UPDATE registrations SET " \
    "lapsPassed = lapsPassed + 1 " \
    "WHERE id = %s " \
    "RETURNING *"

updateRegistrationById = \
    "UPDATE registrations SET " \
    "isConfirmed = %s, " \
    "adminComment = %s, " \
    "level = %s, " \
    "salary = %s, " \
    "taskText = %s, " \
    "lapsPassed = %s, " \
    "cameDate = %s, " \
    "leaveDate = %s " \
    "WHERE id = %s " \
    "RETURNING *"

# ------------------

deleteEventById = \
    "DELETE FROM events " \
    "WHERE id = %s"

deleteRegistrationByEventidUserid = \
    "DELETE FROM registrations " \
    "WHERE eventId = %s AND userId = %s"
