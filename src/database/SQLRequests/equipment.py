# ----- INSERTS -----

insertEquipment = \
    "INSERT INTO equipment (title, description, previewUrl, amountTotal, isNeedsToReturn, eventId) " \
    "VALUES (%s, %s, %s, %s, %s, %s) " \
    "RETURNING *"

insertUserEquipment = \
    "INSERT INTO usersequipments (userId, equipmentId, amountHolds) " \
    "VALUES (%s, %s, %s) " \
    "RETURNING *"


# ----- SELECTS -----
selectEquipmentById = \
    "SELECT * FROM equipment " \
    "WHERE id = %s"

selectEquipmentsGroupsByEventId = \
    "SELECT equipment.title, equipment.description, equipment.isneedstoreturn, equipment.previewurl, SUM(amountTotal) as amountTotal, SUM(amountTotal) - COALESCE(SUM(ue.amountHolds), 0) as amountLeft FROM equipment " \
    "LEFT JOIN usersEquipments ue ON ue.equipmentId = equipment.id " \
    "WHERE equipment.eventId = %s " \
    "GROUP BY equipment.title, equipment.description, equipment.isneedstoreturn, equipment.previewurl"

selectEquipmentsByEventId = \
    "SELECT equipment.*, amountTotal - COALESCE(SUM(ue.amountHolds), 0) as amountLeft FROM equipment " \
    "LEFT JOIN usersEquipments ue ON ue.equipmentId = equipment.id " \
    "WHERE equipment.eventId = %s " \
    "GROUP BY equipment.id"

selectEquipmentWithAmountLeftById = \
    "SELECT equipment.*, amountTotal - COALESCE(SUM(ue.amountHolds), 0) as amountLeft FROM equipment " \
    "LEFT JOIN usersEquipments ue ON ue.equipmentId = equipment.id " \
    "WHERE equipment.id = %s " \
    "GROUP BY equipment.id"

selectEquipmentUsersHoldersByEquipmentIdEventId = \
    "SELECT users.id, (users.givenName  || ' ' || users.familyName) as username, users.avatarUrl FROM usersEquipments " \
    "LEFT JOIN users ON usersEquipments.userId = users.id " \
    "WHERE usersEquipments.equipmentId = %s " \
    "AND eventId = %s"

selectUserEquipmentsByUseridEquipmentId = \
    "SELECT usersequipments.*, equipment.title, equipment.previewUrl, equipment.isNeedsToReturn  FROM usersequipments " \
    "JOIN equipment on usersequipments.equipmentid = equipment.id " \
    "WHERE userid = %s " \
    "AND equipmentid = %s " \
    "ORDER BY takenDate"


updateEquipmentById = \
    "UPDATE equipment " \
    "SET title = %s, " \
    "description = %s, " \
    "previewUrl = %s, " \
    "amountTotal = %s " \
    "isNeedsToReturn = %s " \
    "WHERE id = %s " \
    "RETURNING *"

updateUserEquipmentAmountHoldsByUseridEquipmentId = \
    "UPDATE usersequipments " \
    "SET amountHolds = %s," \
    "updatedDate = NOW() " \
    "WHERE userid = %s " \
    "AND equipmentid = %s " \
    "RETURNING *"


# ----- DELETES -----

deleteEquipmentById = \
    "DELETE FROM equipment " \
    "WHERE id = %s"

deleteUserEquipmentById = \
    "DELETE FROM usersequipments " \
    "WHERE id = %s"

deleteUserEquipmentByEquipmentId = \
    "DELETE FROM usersequipments " \
    "WHERE equipmentId = %s"

deleteUserEquipmentByUseridEquipmentId = \
    "DELETE FROM usersequipments " \
    "WHERE userid = %s " \
    "AND equipmentid = %s"
