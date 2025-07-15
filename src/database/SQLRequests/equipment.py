# ----- INSERTS -----

insertEquipment = \
    "INSERT INTO equipments (title, description, previewUrl, amountTotal, isNeedsToReturn, eventId) " \
    "VALUES (%s, %s, %s, %s, %s, %s) " \
    "RETURNING *"

insertUserEquipment = \
    "INSERT INTO usersequipments (userId, equipmentId, amountHolds) " \
    "VALUES (%s, %s, %s) " \
    "RETURNING *"


# ----- SELECTS -----
selectEquipmentById = \
    "SELECT * FROM equipments " \
    "WHERE id = %s"

selectEquipmentsByEventId = \
    "SELECT equipments.*, amountTotal - SUM(usersEquipments.amountHolds) as amountLeft FROM equipments " \
    "JOIN usersEquipments ue ON ue.equipmentId = equipments.id" \
    "WHERE usersEquipments.eventId = %s "
    # "GROUP BY equipments.title"

selectEquipmentUsersHoldersByEquipmentIdEventId = \
    "SELECT users.id, (users.givenName  || ' ' || users.familyName) as username, users.avatarUrl FROM usersEquipments " \
    "JOIN users ON usersEquipments.userId = users.id " \
    "WHERE usersEquipments.equipmentId = %s" \
    "AND eventId = %s"

selectUserEquipmentsByUseridEventId = \
    "SELECT usersequipments.*, equipments.title, equipment.previewUrl  FROM usersequipments " \
    "JOIN equipments on usersequipments.equipmentid = equipments.id " \
    "WHERE userid = %s " \
    "AND eventId = %s" \
    "ORDER BY takenDate"


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
