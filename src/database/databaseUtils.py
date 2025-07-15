from src.connections import DB
from src.database.SQLRequests import history as SQLHistory

def insertHistory(userId, type, text):
    DB.execute(SQLHistory.insertHistory, [userId, type, text])
