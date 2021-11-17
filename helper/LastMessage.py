

class LastMessage:
    def __init__(self, message):
        self.message = message
        self.user = message.author
        self.server = message.guild

    def get_message(self):
        return self.message

    def get_user(self):
        return self.user

    def get_server(self):
        return self.server

    def check_if_time_passed(self, ):
        return self.message.created_at < time
