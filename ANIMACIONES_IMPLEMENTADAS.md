# 🎨 Animaciones Implementadas en el Proyecto

## ✨ **Resumen de Animaciones**

Se han agregado animaciones suaves y transiciones fluidas a todo el proyecto para mejorar la experiencia de usuario. Las animaciones incluyen:

### 🎯 **Tipos de Animaciones**

1. **Animaciones de Entrada**
   - `fadeInUp`: Elementos que aparecen desde abajo
   - `fadeIn`: Elementos que aparecen gradualmente
   - `slideInRight`: Elementos que se deslizan desde la derecha
   - `slideInLeft`: Elementos que se deslizan desde la izquierda
   - `scaleIn`: Elementos que se escalan al aparecer
   - `bounceIn`: Elementos que rebotan al aparecer

2. **Animaciones de Interacción**
   - Hover effects en botones y tarjetas
   - Transiciones suaves en inputs y formularios
   - Animaciones de carga y estados
   - Efectos de pulso para elementos importantes

3. **Animaciones de Scroll**
   - Elementos que aparecen al hacer scroll
   - Animaciones escalonadas (staggered)
   - Efectos de parallax suaves

## 🎬 **Animaciones por Sección**

### **Frontend del Cliente**

#### **Hero Section**
- Animación de entrada: `fadeInUp`
- Botón flotante: `bounceIn` con hover effects

#### **Gallery Section**
- Animación de entrada: `slideInRight` con delay
- Imágenes con hover effects

#### **Work Section**
- Animación de entrada: `slideInLeft` con delay
- Tarjetas con hover effects

#### **Location Section**
- Animación de entrada: `fadeInUp` con delay

#### **Modal de Booking**
- Apertura: `scaleIn`
- Cierre: `scaleIn` reverse
- Pasos del formulario: `fadeInUp`

#### **Calendario**
- Días: Hover effects y selección
- Horarios: Hover y selección con `bounceIn`

#### **WhatsApp Float**
- Entrada: `bounceIn` con delay
- Hover: Rotación y escala

### **Frontend del Barbero**

#### **Dashboard**
- Header: `fadeInUp`
- Estadísticas: `bounceIn` escalonado
- Sección de turnos: `fadeInUp` con delay
- Tarjetas de turnos: Hover effects

#### **Calendario Mensual**
- Modal: `scaleIn`
- Navegación: `fadeInUp`
- Días: Hover effects
- Detalles del día: `fadeInUp`

#### **Login**
- Contenedor: `fadeInUp`
- Formulario: `scaleIn` con delay

## 🛠️ **Componentes y Hooks**

### **AnimatedElement Component**
```jsx
<AnimatedElement 
  animation="fade-in-up" 
  delay={2} 
  className="my-class"
>
  Contenido animado
</AnimatedElement>
```

### **useScrollAnimation Hook**
```jsx
const scrollRef = useScrollAnimation();
return <div ref={scrollRef} className="fade-in-on-scroll">...</div>;
```

## 🎨 **Clases CSS Disponibles**

### **Animaciones de Entrada**
- `.animate-fade-in`
- `.animate-fade-in-up`
- `.animate-slide-in-right`
- `.animate-slide-in-left`
- `.animate-scale-in`
- `.animate-bounce-in`

### **Delays Escalonados**
- `.stagger-1` (0.1s)
- `.stagger-2` (0.2s)
- `.stagger-3` (0.3s)
- `.stagger-4` (0.4s)
- `.stagger-5` (0.5s)

### **Estados Especiales**
- `.pulse` - Animación de pulso
- `.shake` - Animación de error
- `.success-animation` - Animación de éxito
- `.fade-out` - Animación de salida

## 📱 **Optimizaciones para Móvil**

- Animaciones reducidas en dispositivos móviles
- Transiciones más rápidas para mejor rendimiento
- Hover effects adaptados para touch
- Scroll suave habilitado

## ⚡ **Rendimiento**

- Uso de `transform` y `opacity` para animaciones GPU-accelerated
- `will-change` para optimizar elementos animados
- Intersection Observer para animaciones de scroll eficientes
- Transiciones CSS en lugar de JavaScript cuando es posible

## 🎯 **Cómo Usar**

### **1. Animaciones Automáticas**
Las animaciones se aplican automáticamente a elementos existentes.

### **2. Usar AnimatedElement**
```jsx
import AnimatedElement from './components/AnimatedElement';

<AnimatedElement animation="bounce-in" delay={1}>
  <div>Contenido animado</div>
</AnimatedElement>
```

### **3. Usar Clases CSS Directamente**
```jsx
<div className="animate-fade-in-up stagger-2">
  Contenido con animación
</div>
```

### **4. Animaciones de Scroll**
```jsx
import { useScrollAnimation } from './hooks/useScrollAnimation';

const MyComponent = () => {
  const scrollRef = useScrollAnimation();
  
  return (
    <div ref={scrollRef} className="fade-in-on-scroll">
      Aparece al hacer scroll
    </div>
  );
};
```

## 🔧 **Personalización**

### **Cambiar Velocidad de Animaciones**
```css
.animate-fade-in-up {
  animation-duration: 0.8s; /* Cambiar duración */
}
```

### **Agregar Nuevas Animaciones**
```css
@keyframes myCustomAnimation {
  from { /* estado inicial */ }
  to { /* estado final */ }
}

.my-custom-animation {
  animation: myCustomAnimation 0.5s ease-out;
}
```

## 📊 **Compatibilidad**

- ✅ Chrome/Edge (WebKit)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers
- ✅ Intersection Observer API (IE11+ con polyfill)

## 🎨 **Paleta de Animaciones**

- **Entrada**: Suave y elegante
- **Interacción**: Responsiva y feedback inmediato
- **Salida**: Rápida y no intrusiva
- **Carga**: Informativa y profesional
- **Error**: Clara y llamativa
- **Éxito**: Satisfactoria y celebrativa

¡Las animaciones hacen que la aplicación se sienta más viva y profesional! 🚀
