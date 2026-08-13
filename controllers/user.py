# ============================================================
# controllers/user.py - Contrôleur des utilisateurs
# ============================================================

from services.user_service import  UserService



class UserController:
    """
    Contrôleur pour les actions liées aux utilisateurs.
    Fait le lien entre la route et le service.
    Ne contient aucune logique métier.
    """

    def __init__(self, db):
        """Initialise le contrôleur avec une session de base de données."""
        self.db = db
        self.service = UserService(db)



    def create_user_account(self, user_data):
        """Crée un nouvel utilisateur."""
        return self.service.create_user_account( user_data)




    def get_all_users(self, skip=0, limit=100):
        """Récupère la liste de tous les utilisateurs (paginé)."""
        return self.service.get_all_users(skip, limit)

    def get_user_by_id(self, user_id):
        """Récupère un utilisateur par son ID."""
        return self.service.get_user_by_id(user_id)

    def get_self_profile(self, user_id):
        """Récupère son propre profil."""
        return self.service.get_user_by_id( user_id)

    def update_user(self, user_id, user_data):
        """Modifie un utilisateur (Admin/Scolarité)."""
        return self.service.update_user(user_id, user_data)

    def update_user_self(self, user_id, user_data):
        """Modifie son propre profil (champs restreints)."""
        return self.service.update_user_self(user_id, user_data)

    def update_password(self, user_id, password_data):
        """Modifie le mot de passe de l'utilisateur connecté."""
        return self.service.update_password( user_id, password_data)

    def delete_user(self, user_id):
        """Supprime un utilisateur (Admin uniquement)."""
        return self.service.delete_user(user_id)

    def renvoyer_token_activation(self, user_id):
        """Renvoie un nouveau token d'activation (Admin/Scolarité)."""
        return self.service.renvoyer_token_activation(user_id)