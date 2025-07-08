# ----- INSERTS -----

insertEquipment = \
    "INSERT INTO equipments (title, description, previewUrl, amountTotal, isNeedsToReturn, eventId) " \
    "VALUES (%s, %s, %s, %s, %s, %s) " \
    "RETURNING *"

insertUserEquipment = \
    "INSERT INTO usersequipments (userId, equipmentId, eventId, amountHolds) " \
    "VALUES (%s, %s, %s, %s) " \
    "RETURNING *"

insertEquipmentsHistory = \
    "INSERT INTO equipmentshistory (eventId, equipmentId, userFromId, userToId, amount) " \
    "VALUES (%s, %s, %s, %s) " \
    "RETURNING *"


# ----- SELECTS -----
selectEquipmentsByEventId = \
    "SELECT equipments.*, amountTotal - SUM(usersEquipments.amountHolds) as amountLeft FROM equipments " \
    "JOIN usersEquipments ue ON ue.equipmentId = equipments.id" \
    "WHERE usersEquipments.eventId = %s"

selectEquipmentUsersHoldersByEquipmentIdEventId = \
    "SELECT users.id, (users.givenName  || ' ' || users.familyName) as username, users.avatarUrl FROM usersEquipments " \
    "JOIN users ON usersEquipments.userId = users.id " \
    "WHERE usersEquipments.equipmentId = %s" \
    "AND eventId = %s"

# %s for title search must be provided as: '%{}%'.format(<YOUR_VAR>)
selectEquipmentBySearchTitleEventId = \
    f"SELECT * FROM equipments " \
    f"WHERE LOWER(title) LIKE %s " \
    f"AND eventId = %s" \
    f"ORDER BY title"

selectUserEquipmentsByUseridEventId = \
    "SELECT usersequipments.*, equipments.title, equipment.previewUrl  FROM usersequipments " \
    "JOIN equipments on usersequipments.equipmentid = equipments.id " \
    "WHERE userid = %s " \
    "AND eventId = %s" \
    "ORDER BY takenDate"

selectEquipmentsHistoryByEventId = \
    "SELECT equipmentshistory.*, equipments.title, equipment.previewUrl, (uf.givenName  || ' ' || uf.familyName) as fromusername, uf.avatarUrl as fromuseravatarurl, (ut.givenName  || ' ' || ut.familyName) as tousername, ut.avatarUrl as touseravatarurl FROM equipmentshistory " \
    "JOIN equipments on equipmentshistory.equipmentid = equipments.id " \
    "JOIN users uf on equipmentshistory.userfromid = uf.id " \
    "JOIN users ut on equipmentshistory.usertoid = ut.id " \
    "WHERE eventid = %s " \
    "ORDER BY date"


# ----- UPDATES -----

updateEquipmentById = \
    "UPDATE equipments " \
    "SET title = %s, " \
    "description = %s, " \
    "previewUrl = %s, " \
    "amountTotal = %s " \
    "isNeedsToReturn = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserEquipmentAmountHoldsById = \
    "UPDATE usersequipments " \
    "SET amountHolds = %s," \
    "updatedDate = NOW() " \
    "WHERE id = %s " \
    "RETURNING *"


# ----- DELETES -----

deleteEquipmentById = \
    "DELETE FROM equipment " \
    "WHERE id = %s"

deleteUserEquipmentById = \
    "DELETE FROM usersequipments " \
    "WHERE id = %s"
