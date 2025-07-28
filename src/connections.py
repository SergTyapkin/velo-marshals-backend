from src.database.database import Database
from src.utils.utils import read_config
from src.TgBot.TgBot import TgBotClass


config = read_config('./configs/config.json')
DB = Database(
    host=config['db_host'],
    port=config['db_port'],
    user=config['db_user'],
    password=config['db_password'],
    dbname=config['db_name'],
)
TgBot = TgBotClass(config)
