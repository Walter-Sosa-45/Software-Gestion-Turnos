# test_turnos.py
from sqlalchemy.orm import Session
from app.core.config import get_db
from app.models.models import Turno, Clientes, Servicio
from datetime import datetime, date, time
import json

def test_turnos():
    """Prueba la creación y consulta de turnos"""
    db = next(get_db())
    
    try:
        # 1. Verificar que existan servicios
        servicios = db.query(Servicio).all()
        print(f"Servicios encontrados: {len(servicios)}")
        for servicio in servicios:
            print(f"- {servicio.nombre}: ${servicio.precio/100:.2f}")
        
        # 2. Verificar que existan clientes
        clientes = db.query(Clientes).all()
        print(f"Clientes encontrados: {len(clientes)}")
        for cliente in clientes:
            print(f"- {cliente.nombre}: {cliente.telefono}")
        
        # 3. Verificar turnos existentes
        turnos = db.query(Turno).all()
        print(f"Turnos existentes: {len(turnos)}")
        
        # 4. Obtener turnos de hoy
        fecha_hoy = date.today()
        turnos_hoy = db.query(Turno).filter(Turno.fecha == fecha_hoy).all()
        print(f"Turnos de hoy ({fecha_hoy}): {len(turnos_hoy)}")
        
        for turno in turnos_hoy:
            print(f"- Turno {turno.id}: {turno.cliente.nombre} - {turno.servicio.nombre} - {turno.hora_inicio} - {turno.estado}")
        
        # 5. Probar la función get_turnos con relaciones
        from app.crud import crud
        turnos_con_relaciones = crud.get_turnos(db, fecha_inicio=fecha_hoy, fecha_fin=fecha_hoy)
        print(f"Turnos con relaciones: {len(turnos_con_relaciones)}")
        
        for turno in turnos_con_relaciones:
            print(f"- {turno.cliente.nombre} - {turno.servicio.nombre} - {turno.hora_inicio}")
        
        # 6. Probar el endpoint de turnos por fecha
        from app.routes.routes import get_turnos_por_fecha
        fecha_str = fecha_hoy.strftime("%Y-%m-%d")
        resultado = get_turnos_por_fecha(fecha_str, db)
        print(f"Resultado del endpoint: {len(resultado['turnos'])} turnos")
        
        for turno in resultado['turnos']:
            print(f"- {turno.cliente.nombre} - {turno.servicio.nombre}")
            
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_turnos()
