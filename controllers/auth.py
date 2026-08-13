

from sqlalchemy.orm import Session
from schemas.user import UserLogin, UserActivate
from services.auth_service import AuthService

class AuthController:
    def __init__(self, db: Session):
        self.auth_service = AuthService(db)

    def login(self, user_data: UserLogin):

        return self.auth_service.login_and_generate_token(user_data)

    def verify_activation_token(self, token: str):

        return self.auth_service.check_token_validity(token)

    def activate_user(self, token: str, password_data: UserActivate):

        return self.auth_service.activate_user_account(token, password_data)
