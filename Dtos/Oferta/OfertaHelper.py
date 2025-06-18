# Dtos/Oferta/OfertaHelper.py

from enum import Enum

class EstadoOferta(str, Enum):
    ACTIVA = "Activa"
    FINALIZADA = "Finalizada"
    PAUSADA = "Pausada"  

def es_oferta_activa(estado: str) -> bool:
    return estado.lower() == EstadoOferta.ACTIVA.lower()

def es_oferta_finalizada(estado: str) -> bool:
    return estado.lower() == EstadoOferta.FINALIZADA.lower()
