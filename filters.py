from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import Union, Dict, Any

import db  # Assuming you have a db module for database operations

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        try:
            state = await db.get_datax(database="admins", user_id=message.from_user.id)
            return state or message.from_user.id == 7217640284  # Your chat_admins ID
        except:
            return False

class IsBanned(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        try:
            state = await db.get_datax(database="banlist", user_id=message.from_user.id)
            return bool(state)
        except:
            return False


class HasBalance(BaseFilter):
    def __init__(self, min_balance: float):
        self.min_balance = min_balance

    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        user = await db.get_datax(database="users", user_id=message.from_user.id)
        if user and float(user['balance']) >= self.min_balance:
            return {"user_balance": float(user['balance'])}
        return False