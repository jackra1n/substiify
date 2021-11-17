from typing import List

from helper.LastMessage import LastMessage

class LastMessageList():
    def __init__(self):
        self.lastMessageList:List[LastMessage] = []

    def addMessage(self, message):
        self.lastMessageList.append(message)

    def getLastMessage(self):
        return self.lastMessageList[-1]

    def getLastMessageByUser(self, user):
        for message in self.lastMessageList:
            if message.get_user() == user:
                return message
        return None

    def getLastMessageByUserAndServer(self, user, server):
        for message in self.lastMessageList:
            if message.get_user() == user and message.get_server() == server:
                return message
        return None