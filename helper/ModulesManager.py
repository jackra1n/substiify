from discord.ext import commands
from utils import db

import logging

logger = logging.getLogger(__name__)

class ModulesManager():
    commands = []

    def register(func):
        if func.__name__ not in ModulesManager.get_commands():
            ModulesManager.commands.append(func.__name__)
        return func

    def get_commands() -> list:
        return ModulesManager.commands

    def is_enabled(ctx) -> bool:
        root_command = ctx.command.root_parent if ctx.command.root_parent is not None else ctx.command
        if ModulesManager._is_enabled(ctx.guild.id, root_command.name):
            return True
        raise ModuleDisabledException()

    def _is_enabled(server_id: int, module: str) -> bool:
        return db.session.query(db.enabled_commands).filter_by(server_id=server_id).filter_by(command=module).first() is not None

    @staticmethod
    def toggle_module(server_id: int, module: str) -> bool:
        if not ModulesManager._is_enabled(server_id, module):
            db.session.add(db.enabled_commands(server_id, module))
            db.session.commit()
            return 'enabled'
        elif ModulesManager._is_enabled(server_id, module):
            db.session.query(db.enabled_commands).filter_by(server_id=server_id, command=module).delete()
            db.session.commit()
            return 'disabled'

class ModuleDisabledException(commands.CommandError):
    pass