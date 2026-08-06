# ============================================================
# core/handlers.py - Gestionnaire de réponses et exceptions
# ============================================================

from typing import Callable
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from schemas.response import ApiResponse


# ---------- Gestionnaire pour les routes ----------
def handle_request(service_func: Callable, success_message: str = "Opération réussie", *args, **kwargs) -> ApiResponse:
    """
    Exécute une fonction de service et retourne une réponse standardisée.

    Args:
        service_func (Callable): La fonction de service à exécuter
        success_message (str): Message de succès personnalisé
        *args: Arguments positionnels pour la fonction
        **kwargs: Arguments nommés pour la fonction

    Returns:
        ApiResponse: Réponse standardisée
    """
    try:
        result = service_func(*args, **kwargs)
        return ApiResponse(
            success=True,
            message=success_message,
            data=result
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