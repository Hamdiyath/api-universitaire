
# exceptions/base.py - Exceptions métier personnalisées

# Ces exceptions sont levées par les services.
# Elles sont interceptées par les gestionnaires globaux dans main.py
# et transformées en réponses HTTP.



class AppError(Exception):
    """
    Classe de base pour toutes les erreurs métier de l'application.
    Toutes les exceptions métier doivent hériter de cette classe.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# ---------- Utilisateurs ----------
class UserNotFoundError(AppError):
    """Levée quand un utilisateur n'est pas trouvé."""
    def __init__(self, user_id: int):
        super().__init__(f"Utilisateur {user_id} non trouvé")


class EmailAlreadyExistsError(AppError):
    """Levée quand un email est déjà utilisé."""
    def __init__(self, email: str):
        super().__init__(f"L'email '{email}' est déjà utilisé")


class AccountAlreadyActiveError(AppError):
    """Levée quand un compte est déjà activé."""
    def __init__(self):
        super().__init__("Ce compte est déjà activé")


class InvalidPasswordError(AppError):
    """Levée quand le mot de passe actuel est incorrect."""
    def __init__(self):
        super().__init__("Mot de passe actuel incorrect")


# ---------- Rôles ----------
class RoleNotFoundError(AppError):
    """Levée quand un rôle n'est pas trouvé."""
    def __init__(self, role_name: str):
        super().__init__(f"Le rôle '{role_name}' n'existe pas")


# ---------- Filières ----------
class FiliereRequiredError(AppError):
    """Levée quand un étudiant est créé sans filière."""
    def __init__(self):
        super().__init__("Une filière est obligatoire pour un étudiant")


class FiliereNotFoundError(AppError):
    """Levée quand une filière n'est pas trouvée."""
    def __init__(self, filiere_id: int):
        super().__init__(f"Filière {filiere_id} non trouvée")


# ---------- Matières ----------
class MatiereNotFoundError(AppError):
    """Levée quand une matière n'est pas trouvée."""
    def __init__(self, matiere_id: int):
        super().__init__(f"Matière {matiere_id} non trouvée")


# ---------- Notes ----------
class NoteNotFoundError(AppError):
    """Levée quand une note n'est pas trouvée."""
    def __init__(self, note_id: int):
        super().__init__(f"Note {note_id} non trouvée")


class NoteModificationDeniedError(AppError):
    """Levée quand un professeur essaie de modifier une note qui n'est pas la sienne."""
    def __init__(self):
        super().__init__("Vous ne pouvez modifier que vos propres notes")


class NoteModificationDelayError(AppError):
    """Levée quand le délai de modification de 7 jours est dépassé."""
    def __init__(self):
        super().__init__("Délai de modification dépassé (7 jours)")


# ---------- Enseignements ----------
class EnseignementNotFoundError(AppError):
    """Levée quand un enseignement n'est pas trouvé."""
    def __init__(self, enseignement_id: int):
        super().__init__(f"Enseignement {enseignement_id} non trouvé")


class EnseignementAlreadyExistsError(AppError):
    """Levée quand un professeur est déjà assigné à une matière."""
    def __init__(self):
        super().__init__("Ce professeur est déjà assigné à cette matière")


# ---------- Inscriptions ----------
class InscriptionNotFoundError(AppError):
    """Levée quand une inscription n'est pas trouvée."""
    def __init__(self):
        super().__init__("Inscription non trouvée")


class InscriptionAlreadyExistsError(AppError):
    """Levée quand un étudiant est déjà inscrit à une matière."""
    def __init__(self):
        super().__init__("Cet étudiant est déjà inscrit à cette matière")


class InscriptionModificationBlockedError(AppError):
    """Levée quand on tente de modifier une inscription alors que des notes y sont déjà rattachées."""
    def __init__(self, message: str = "Impossible de modifier cette inscription : des notes ont déjà été saisies pour cette matière"):
        self.message = message
        super().__init__(self.message)


# ---------- Semestres ----------
class SemestreNotFoundError(AppError):
    """Levée quand un semestre n'existe pas."""
    def __init__(self, semestre: str):
        super().__init__(f"Semestre '{semestre}' non trouvé")


# ---------- Associations ----------
class MatiereFiliereNotFoundError(AppError):
    """Levée quand une association matière-filière n'est pas trouvée."""
    def __init__(self):
        super().__init__("Association matière-filière non trouvée")


class MatiereFiliereAlreadyExistsError(AppError):
    """Levée quand une matière est déjà associée à une filière."""
    def __init__(self):
        super().__init__("Cette matière est déjà associée à cette filière pour ce semestre")


class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__("Identifiants invalides ou session expirée.")

class AccountSuspendedError(AppError):
    def __init__(self):
        super().__init__("Votre compte est inactif ou suspendu.")

class AccountNotActivatedError(AppError):
    def __init__(self):
        super().__init__("Compte non activé. Veuillez vérifier vos emails.")

class InsufficientPermissionsError(AppError):
    def __init__(self, required_roles: list[str]):
        super().__init__(f"Accès refusé. Rôles requis : {required_roles}")


class MatriculeAlreadyExistsError(AppError):
    """Levée quand un matricule étudiant est déjà attribué."""
    def __init__(self, matricule: str):
        super().__init__(
            f"Le matricule '{matricule}' est déjà attribué à un autre étudiant."

        )




# ---------- Authentification & Tokens ----------

class PasswordsDoNotMatchError(AppError):
    """Levée quand le mot de passe et sa confirmation ne sont pas identiques."""
    def __init__(self):
        super().__init__("Les deux mots de passe saisis ne correspondent pas.")


class TokenNotFoundError(AppError):
    """Levée quand le token d'activation n'existe pas en base de données."""
    def __init__(self):
        super().__init__("Le token d'activation fourni est invalide ou inexistant.")


class TokenExpiredError(AppError):
    """Levée quand le délai de 24h pour activer le compte est dépassé."""
    def __init__(self):
        super().__init__("Ce token d'activation a expiré. Veuillez contacter la scolarité pour en générer un nouveau.")


# ---------- Sécurité & Autorisations ----------
class RoleAlreadyExistsError(AppError):
    """Levée lors de la création d'un rôle si le nom est déjà pris."""
    def __init__(self, role_name: str):
        super().__init__(
            f"Le rôle '{role_name}' existe déjà dans le système universitaire."

        )


class PermissionDeniedError(AppError):
    """Levée quand l'utilisateur n'a pas la permission d'effectuer une action."""
    def __init__(self, message: str = "Vous n'avez pas l'autorisation d'effectuer cette action"):
        self.message = message
        super().__init__(self.message)



class MatiereAlreadyExistsError(AppError):
    """Levée quand une matière avec ce nom existe déjà."""
    def __init__(self, nom: str):
        self.message = f"Une matière avec le nom '{nom}' existe déjà"
        super().__init__(self.message)


class FiliereAlreadyExistsError(AppError):
    """Levée quand une filière avec ce nom existe déjà."""
    def __init__(self, nom: str ):
        self.message = f"Une filière avec le nom '{nom}' existe déjà"
        super().__init__(self.message)



# ---------- Résultats Matières ----------
class ResultatMatiereNotFoundError(AppError):
    """Levée quand une ligne de résultat matière n'est pas trouvée."""
    def __init__(self, message: str = "Résultat de matière non trouvé"):
        self.message = message
        super().__init__(self.message)


class DecisionAnnuelleAlreadyExistsError(AppError):
    """Levée quand une décision annuelle existe déjà pour cet étudiant et cette année."""
    def __init__(self, message: str = "Une décision de passage existe déjà pour cet étudiant pour cette année"):
        self.message = message
        super().__init__(self.message)


class DecisionAnnuelleNotFoundError(AppError):
    """Levée quand une décision annuelle n'est pas trouvée."""
    def __init__(self, message: str = "Décision annuelle non trouvée"):
        self.message = message
        super().__init__(self.message)