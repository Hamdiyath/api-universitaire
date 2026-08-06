# ============================================================
# core/handlers.py - Gestionnaire de réponses et exceptions
# ============================================================

from typing import Callable
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from schemas.response import ApiResponse


# ---------- Gestionnaire pour les routes ----------
def handle_request(service_func: Callable, success_message: str = "Opération réussie", *args, **kwargs) -> ApiResponse:
    """
    Exécute une fonction de service et retourne une réponse standardisée.
    """
    try:
        result = service_func(*args, **kwargs)
        return ApiResponse(
            success=True,
            message=success_message,
            data=result
        )
    except IntegrityError as e:
        # Gestion des erreurs d'intégrité de la base de données
        if "UNIQUE constraint" in str(e):
            return ApiResponse(
                success=False,
                message="Cette valeur est déjà utilisée (contrainte d'unicité)",
                data=None
            )
        return ApiResponse(
            success=False,
            message=f"Erreur d'intégrité de la base de données: {str(e)}",
            data=None
        )
    except HTTPException as e:
        return ApiResponse(
            success=False,
            message=e.detail,
            data=None
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            message=f"Erreur interne du serveur: {str(e)}",
            data=None
        )


# ---------- Gestionnaire pour les exceptions globales ----------
def setup_exception_handlers(app: FastAPI):
    """
    Enregistre tous les handlers d'exceptions globaux sur l'application FastAPI.
    """

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.detail, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "message": "Données d'entrée invalides ou manquantes", "data": None},
        )

    @app.exception_handler(Exception)
    async def global_internal_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Erreur interne du serveur", "data": None},
        )