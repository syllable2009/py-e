from .email_service import EmailService

class UserService:
    def __init__(self, emailer: EmailService):
        self.emailer = emailer

    def register_user(self, email: str):
        print(f"👤 Registering user: {email}")
        self.emailer.send(email, "Welcome!")