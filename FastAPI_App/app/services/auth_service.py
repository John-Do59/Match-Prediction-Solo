from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User
from ..schemas.user import UserRegister, UserLogin
from ..core.security import get_password_hash, verify_password, create_access_token


class AuthService:
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def register_user(db: Session, user_data: UserRegister):
        # Check if email exists
        if AuthService.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé.",
            )

        # Check if username exists
        if AuthService.get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom d'utilisateur est déjà pris.",
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin):
        user = AuthService.get_user_by_email(db, login_data.email)
        if not user:
            return False
        if not verify_password(login_data.password, user.hashed_password):
            return False
        return user

    @staticmethod
    def create_user_token(user: User):
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    def update_user_profile(db: Session, user: User, update_data: dict):
        if "email" in update_data and update_data["email"] != user.email:
            if AuthService.get_user_by_email(db, update_data["email"]):
                raise HTTPException(status_code=400, detail="Email déjà utilisé")
        
        for key, value in update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user_account(db: Session, user: User):
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def change_user_password(db: Session, user: User, old_pwd: str, new_pwd: str):
        if not verify_password(old_pwd, user.hashed_password):
            raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
        
        user.hashed_password = get_password_hash(new_pwd)
        db.commit()
        return True

    @staticmethod
    def forgot_password(db: Session, email: str):
        user = AuthService.get_user_by_email(db, email)
        if not user:
            # Sécurité: ne pas révéler si l'email existe
            return {"message": "Si l'adresse existe, un lien a été envoyé."}
        
        # Envoi de l'email via le service dédié
        from ..core.email import send_password_reset_email
        
        reset_token = create_access_token(
            data={"sub": user.email, "type": "reset"},
            expires_delta=timedelta(minutes=15)
        )
        
        send_password_reset_email(user.email, reset_token)
        
        return {"message": "Si l'adresse existe, un lien a été envoyé."}

    @staticmethod
    def reset_password_with_token(db: Session, token: str, new_pwd: str):
        from jose import jwt, JWTError
        from ..core.config import settings

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            if not email or payload.get("type") != "reset":
                raise HTTPException(status_code=400, detail="Token invalide")
        except JWTError:
            raise HTTPException(status_code=400, detail="Token invalide ou expiré")
        
        user = AuthService.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
        user.hashed_password = get_password_hash(new_pwd)
        db.commit()
        return True
