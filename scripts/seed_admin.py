# ============================================================
# scripts/seed_admin.py - Script de création des rôles et du compte admin
# ============================================================
# Ce script est exécuté automatiquement au démarrage de l'API.
# Il crée les rôles par défaut (admin, scolarite, etudiant, professeur)
# s'ils n'existent pas, puis crée le compte admin.
# ============================================================

import os
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from database import SessionLocal
from models.user import User
from models.role import Role
from core.security import hash_password


def seed_admin():
    """
    Crée les rôles par défaut et un compte administrateur s'ils n'existent pas.
    Les identifiants de l'admin sont lus depuis les variables d'environnement (.env).
    """
    # Récupération des variables d'environnement
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_nom = os.getenv("ADMIN_NOM", "Admin")
    admin_prenom = os.getenv("ADMIN_PRENOM", "System")

    # Vérification que les variables sont définies
    if not admin_email or not admin_password:
        print("⚠️  ADMIN_EMAIL ou ADMIN_PASSWORD non définis dans .env")
        print("   Le compte admin n'a pas été créé.")
        return

    db = SessionLocal()

    try:
        # ----- ÉTAPE 1 : Création des rôles par défaut -----
        roles_par_defaut = ["admin", "scolarite", "etudiant", "professeur"]

        for role_name in roles_par_defaut:
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                new_role = Role(name=role_name, description=f"Rôle {role_name}")
                db.add(new_role)
                print(f"✅ Rôle '{role_name}' créé avec succès")

        db.commit()

        # ----- ÉTAPE 2 : Récupération du rôle admin -----
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            print("⚠️  Le rôle 'admin' n'a pas pu être créé.")
            return

        # ----- ÉTAPE 3 : Création du compte admin -----
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print(f"✅ Compte admin déjà existant : {admin_email}")
            return

        # Hacher le mot de passe
        hashed_password = hash_password(admin_password)

        # Créer le compte admin
        new_admin = User(
            email=admin_email,
            password_hash=hashed_password,
            nom=admin_nom,
            prenom=admin_prenom,
            is_active=True,
            statut="actif",
            created_at=func.now(),
            updated_at=func.now()
        )

        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        # Associer le rôle "admin"
        new_admin.roles.append(admin_role)
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        print(f"✅ Compte admin créé avec succès : {admin_email}")
        print(f"   Nom : {admin_nom} {admin_prenom}")
        print("   🔑 Conservez ces identifiants précieusement.")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la création : {str(e)}")
    finally:
        db.close()