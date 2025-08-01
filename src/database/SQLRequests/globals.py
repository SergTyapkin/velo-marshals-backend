# ----- INSERTS -----
insertGlobals = \
    "INSERT INTO globals (inEventId, isOnMaintenance) " \
    "VALUES (NULL, FALSE) " \
    f"RETURNING *"

# ----- SELECTS -----
selectGlobals = \
    f"SELECT * FROM globals"

selectGlobalEvent = \
    f"SELECT * FROM globals " \
    f"JOIN events ON globals.inEventId = events.id "

selectGlobalRegistrationByUserId = \
    f"SELECT * FROM globals " \
    f"JOIN registrations ON globals.inEventId = registrations.eventid " \
    f"AND registrations.userid = %s"

# ----- UPDATES -----
updateGlobals = \
    "UPDATE globals SET " \
    "inEventId = %s, " \
    "isOnMaintenance = %s " \
    "RETURNING *"
