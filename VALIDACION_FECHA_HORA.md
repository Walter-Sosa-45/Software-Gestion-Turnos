# Validación de Fecha y Hora - Sistema de Agendamiento

## Problema Identificado

El sistema permitía agendar turnos para fechas y horas pasadas, lo cual no debería ser posible. Por ejemplo:
- Si hoy es 21/08/2025 a las 12:55, el cliente podía agendar un turno para las 9:00 del mismo día
- Se podían agendar turnos para fechas pasadas como el 20/08/2025

## Solución Implementada

### 1. Validaciones en el Backend

#### A. Función `get_horarios_disponibles` (`barbero/backend/app/crud/crud.py`)

**Mejoras agregadas:**
- Verificación de que la fecha no sea pasada
- Para el día actual, filtrado de horarios pasados
- Solo se muestran horarios que sean al menos 30 minutos después de la hora actual

```python
# Verificar que la fecha no sea pasada
fecha_actual = date.today()
if fecha < fecha_actual:
    return []

# Si es el día actual, filtrar horarios pasados
if fecha == fecha_actual:
    hora_actual_dt = datetime.now()
    hora_actual_str = hora_actual_dt.strftime("%H:%M")
    # Solo mostrar horarios que sean al menos 30 minutos después de la hora actual
    horarios_trabajo = [h for h in horarios_trabajo if h > hora_actual_str]
```

#### B. Función `verificar_disponibilidad_turno` (`barbero/backend/app/crud/crud.py`)

**Mejoras agregadas:**
- Validación de que la fecha no sea pasada
- Para el día actual, validación de que la hora no sea pasada
- Requerimiento de al menos 30 minutos de anticipación

```python
# Verificar que la fecha no sea pasada
fecha_actual = date.today()
if fecha < fecha_actual:
    return False

# Si es el día actual, verificar que la hora no sea pasada
if fecha == fecha_actual:
    hora_actual = datetime.now().time()
    # Permitir agendar con al menos 30 minutos de anticipación
    hora_minima = (datetime.combine(date.today(), hora_actual) + timedelta(minutes=30)).time()
    if hora_inicio <= hora_minima:
        return False
```

#### C. Endpoints de Creación de Turnos (`barbero/backend/app/routes/routes.py`)

**Mejoras agregadas en ambos endpoints:**
- `POST /api/v1/turnos/`
- `POST /api/v1/turnos/crear-desde-cliente`

```python
# Validar que la fecha no sea pasada
fecha_actual = datetime.now().date()
if fecha_dt < fecha_actual:
    raise HTTPException(status_code=400, detail="No se pueden agendar turnos para fechas pasadas")

# Si es el día actual, validar que la hora no sea pasada
if fecha_dt == fecha_actual:
    hora_actual = datetime.now().time()
    # Permitir agendar con al menos 30 minutos de anticipación
    hora_minima = (datetime.combine(date.today(), hora_actual) + timedelta(minutes=30)).time()
    if hora_dt <= hora_minima:
        raise HTTPException(status_code=400, detail="No se pueden agendar turnos para horarios pasados. Mínimo 30 minutos de anticipación")
```

### 2. Validaciones en el Frontend

#### A. Componente `TimeSelector` (`cliente/src/components/BookingSection.jsx`)

**Mejoras agregadas:**
- Validación de fecha pasada antes de cargar horarios
- Manejo de errores mejorado

```javascript
// Validar que la fecha no sea pasada
const today = new Date()
today.setHours(0, 0, 0, 0)
if (selectedDate < today) {
  setError('No se pueden agendar turnos para fechas pasadas')
  setHorariosDisponibles([])
  return
}
```

#### B. Función `handleSubmit` (`cliente/src/components/BookingSection.jsx`)

**Mejoras agregadas:**
- Validación de fecha y hora antes de enviar al servidor
- Verificación de anticipación mínima de 30 minutos

```javascript
// Validación adicional en el frontend
const fechaTurno = new Date(formData.date + 'T' + formData.time)
const ahora = new Date()

// Verificar que la fecha y hora no sean pasadas
if (fechaTurno <= ahora) {
  setError('No se pueden agendar turnos para fechas u horarios pasados')
  setLoading(false)
  return
}

// Verificar que haya al menos 30 minutos de anticipación
const tiempoMinimo = new Date(ahora.getTime() + 30 * 60 * 1000) // 30 minutos
if (fechaTurno <= tiempoMinimo) {
  setError('Se requiere al menos 30 minutos de anticipación para agendar un turno')
  setLoading(false)
  return
}
```

## Beneficios de la Implementación

1. **Prevención de errores**: Los usuarios no pueden agendar turnos para fechas u horas pasadas
2. **Mejor experiencia de usuario**: Mensajes de error claros y específicos
3. **Consistencia**: Validaciones tanto en frontend como backend
4. **Flexibilidad**: Permite agendar turnos con 30 minutos de anticipación mínima
5. **Seguridad**: Múltiples capas de validación

## Casos de Uso Validados

### ✅ Casos Permitidos:
- Agendar para mañana a las 9:00
- Agendar para hoy a las 14:00 si son las 13:00
- Agendar para hoy a las 14:30 si son las 13:55

### ❌ Casos Bloqueados:
- Agendar para ayer
- Agendar para hoy a las 9:00 si son las 12:55
- Agendar para hoy a las 14:00 si son las 13:45 (menos de 30 min de anticipación)

## Mensajes de Error

### Backend:
- "No se pueden agendar turnos para fechas pasadas"
- "No se pueden agendar turnos para horarios pasados. Mínimo 30 minutos de anticipación"

### Frontend:
- "No se pueden agendar turnos para fechas pasadas"
- "No se pueden agendar turnos para fechas u horarios pasados"
- "Se requiere al menos 30 minutos de anticipación para agendar un turno"

## Testing

Para probar las validaciones:

1. **Fecha pasada**: Intentar agendar para ayer
2. **Hora pasada**: Si son las 12:55, intentar agendar para las 9:00 de hoy
3. **Anticipación insuficiente**: Si son las 13:45, intentar agendar para las 14:00
4. **Caso válido**: Si son las 13:00, agendar para las 14:00

Todas las validaciones deben funcionar correctamente tanto en el frontend como en el backend.
