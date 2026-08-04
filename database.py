# ============================================================
# database.py - Connexion et gestion de la base de données
# ============================================================
# Ce fichier configure la connexion à la base de données via
# SQLAlchemy. Il fournit :
#   - Le moteur (engine) pour exécuter les requêtes
#   - La session (SessionLocal) pour les transactions
#   - La base déclarative (Base) pour définir les modèles
#   - La dépendance get_db() pour l'injection dans FastAPI
# ============================================================

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# ---------- Configuration des logs ----------
# Active les logs SQLAlchemy uniquement en mode debug
if settings.debug:
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# ---------- Construction du moteur ----------
# Le moteur est le point d'entrée de SQLAlchemy.
# Il gère le pool de connexions et traduit le SQL en appels DB.

# Paramètres de connexion spécifiques selon le type de base
connect_args = {}

# Si c'est SQLite (fichier .db), on autorise les accès multi-threads
# car SQLite ne supporte pas nativement plusieurs threads.
# PostgreSQL et MySQL n'ont pas besoin de ce paramètre.
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,  # Affiche les requêtes SQL en debug
    pool_pre_ping=True,  # Vérifie la connexion avant chaque requête
    pool_recycle=3600,  # Recyclage des connexions toutes les heures
)

# ---------- Création de la session ----------
# SessionLocal est une fabrique de sessions.
# Chaque session représente une transaction avec la base.
SessionLocal = sessionmaker(
    autocommit=False,  # Désactive l'autocommit (on gère manuellement)
    autoflush=False,  # Désactive le flush automatique
    bind=engine,  # Lie la session au moteur
)

# ---------- Base déclarative ----------
# Base est la classe mère de tous les modèles (tables).
# Chaque modèle hérite de Base pour être reconnu par SQLAlchemy.
Base = declarative_base()


# ---------- Dépendance FastAPI ----------
# get_db() est utilisée dans les routes FastAPI avec Depends().
# Elle crée une session, la met à disposition de la route,
# puis la ferme automatiquement une fois la requête terminée.
def get_db():
    """
    Dépendance pour obtenir une session de base de données.

    Usage dans une route FastAPI :
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()

    La session est automatiquement fermée à la fin de la requête.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()  # Annule la transaction en cas d'erreur
        raise
    finally:
        db.close()  # Ferme la session (libère la connexion)


# ---------- Fonction utilitaire : création des tables ----------
def create_tables():
    """
    Crée toutes les tables en base de données si elles n'existent pas.
    À appeler au démarrage (ou via Alembic pour les migrations).
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès")


# ---------- Fonction utilitaire : suppression des tables ----------
def drop_tables():
    """
    Supprime toutes les tables (⚠️ DANGER : perte de données).
    À utiliser uniquement en développement ou pour les tests.
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Toutes les tables ont été supprimées")