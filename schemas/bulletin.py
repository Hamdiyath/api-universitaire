from pydantic import BaseModel

class CloturerSemestreRequest(BaseModel):
    etudiant_id: int
    semestre: str
    annee_universitaire: str