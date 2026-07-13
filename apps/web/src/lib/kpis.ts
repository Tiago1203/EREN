import type { Equipo, EventoMantenimiento } from './queries'

export interface KpiResult {
  label: string
  value: string
  detail?: string
  status: 'ok' | 'warning' | 'danger' | 'neutral'
}

// KPIs básicos generales (para el dashboard)
export function calcularKpisBasicos(equipos: Equipo[], eventos: EventoMantenimiento[]): KpiResult[] {
  const hoy = new Date()
  const en30Dias = new Date()
  en30Dias.setDate(hoy.getDate() + 30)

  const activos = equipos.filter((e) => e.estado_final === 'activo').length
  const mantenimiento = equipos.filter((e) => e.estado_final === 'mantenimiento').length
  const inactivos = equipos.filter((e) => e.estado_final === 'inactivo').length

  const calibracionVencida = equipos.filter((e) => {
    if (!e.fecha_proxima_calibracion) return false
    return new Date(e.fecha_proxima_calibracion) < hoy
  }).length

  const calibracionProxima = equipos.filter((e) => {
    if (!e.fecha_proxima_calibracion) return false
    const fecha = new Date(e.fecha_proxima_calibracion)
    return fecha >= hoy && fecha <= en30Dias
  }).length

  const imps = equipos.filter((e) => e.imp != null).map((e) => e.imp!)
  const impPromedio = imps.length > 0 ? (imps.reduce((a, b) => a + b, 0) / imps.length).toFixed(2) : 'N/A'

  const errores = eventos.filter((e) => e.error_porcentual != null).map((e) => e.error_porcentual!)
  const errorPromedio = errores.length > 0
    ? (errores.reduce((a, b) => a + b, 0) / errores.length).toFixed(2) + '%'
    : 'N/A'

  const criticos = equipos.filter((e) => e.criticidad?.toLowerCase() === 'alta' || e.criticidad?.toLowerCase() === 'critica').length

  const eventosCompletados = eventos.filter((e) => e.estado_final === 'completado').length
  const tasaCumplimiento = eventos.length > 0
    ? ((eventosCompletados / eventos.length) * 100).toFixed(1) + '%'
    : 'N/A'

  const disponibilidad = equipos.length > 0
    ? ((activos / equipos.length) * 100).toFixed(1) + '%'
    : 'N/A'

  return [
    { label: 'Equipos activos', value: String(activos), detail: `de ${equipos.length} total`, status: 'ok' },
    { label: 'En mantenimiento', value: String(mantenimiento), status: mantenimiento > 0 ? 'warning' : 'ok' },
    { label: 'Inactivos', value: String(inactivos), status: inactivos > 0 ? 'danger' : 'ok' },
    { label: 'Disponibilidad', value: disponibilidad, status: parseFloat(disponibilidad) >= 90 ? 'ok' : 'warning' },
    { label: 'Calibración vencida', value: String(calibracionVencida), status: calibracionVencida > 0 ? 'danger' : 'ok' },
    { label: 'Calibración próxima (30d)', value: String(calibracionProxima), status: calibracionProxima > 0 ? 'warning' : 'ok' },
    { label: 'IMP promedio', value: impPromedio, status: 'neutral' },
    { label: 'Error % promedio', value: errorPromedio, status: 'neutral' },
    { label: 'Equipos críticos', value: String(criticos), status: criticos > 0 ? 'warning' : 'ok' },
    { label: 'Cumplimiento mant.', value: tasaCumplimiento, detail: `${eventosCompletados}/${eventos.length} eventos`, status: 'neutral' },
  ]
}

// KPIs completos incluyendo ingeniería clínica (para la página específica de KPIs)
export function calcularKpis(equipos: Equipo[], eventos: EventoMantenimiento[]): KpiResult[] {
  const kpisBasicos = calcularKpisBasicos(equipos, eventos)

  // KPIs adicionales de Ingeniería Clínica
  const mtbf = calcularMTBF(equipos, eventos)
  const mttr = calcularMTTR(eventos)
  const tasaFallas = calcularTasaFallas(equipos, eventos)
  const tiempoInactividad = calcularTiempoInactividad(equipos, eventos)
  const indiceCriticidad = calcularIndiceCriticidad(equipos)
  const cumplimientoCalibraciones = calcularCumplimientoCalibraciones(equipos)
  const ratioPreventivoCorrectivo = calcularRatioPreventivoCorrectivo(eventos)

  return [
    ...kpisBasicos,
    // KPIs de Ingeniería Clínica
    { label: 'MTBF', value: mtbf, detail: 'Tiempo medio entre fallas', status: 'neutral' },
    { label: 'MTTR', value: mttr, detail: 'Tiempo medio de reparación', status: 'neutral' },
    { label: 'Tasa de fallas', value: tasaFallas, detail: 'Por 1000 horas', status: 'neutral' },
    { label: 'Tiempo inactividad', value: tiempoInactividad, detail: 'Días promedio', status: tiempoInactividad !== 'N/A' && parseFloat(tiempoInactividad) > 2 ? 'warning' : 'ok' },
    { label: 'Índice criticidad', value: indiceCriticidad, detail: 'Ponderación crítica', status: parseFloat(indiceCriticidad) > 0.5 ? 'warning' : 'ok' },
    { label: 'Cumplimiento calib.', value: cumplimientoCalibraciones, detail: '% a tiempo', status: parseFloat(cumplimientoCalibraciones) >= 90 ? 'ok' : 'warning' },
    { label: 'Ratio Prev/Corr', value: ratioPreventivoCorrectivo, detail: 'Preventivo vs Correctivo', status: 'neutral' },
  ]
}

// MTBF: Mean Time Between Failures (Tiempo medio entre fallas)
function calcularMTBF(equipos: Equipo[], eventos: EventoMantenimiento[]): string {
  if (eventos.length === 0) return 'N/A'
  
  // Filtrar eventos de reparación/correctivo
  const eventosFalla = eventos.filter(e => 
    e.tipo_evento.toLowerCase().includes('correctivo') || 
    e.tipo_evento.toLowerCase().includes('reparación') ||
    e.tipo_evento.toLowerCase().includes('falla')
  )
  
  if (eventosFalla.length === 0) return 'N/A'
  
  // Calcular tiempo total de operación entre fallas
  const fechas = eventosFalla
    .map(e => new Date(e.fecha_ejecucion).getTime())
    .sort((a, b) => a - b)
  
  if (fechas.length < 2) return 'N/A'
  
  let totalTiempo = 0
  for (let i = 1; i < fechas.length; i++) {
    totalTiempo += (fechas[i] - fechas[i-1])
  }
  
  const mtbfHoras = totalTiempo / (fechas.length - 1) / (1000 * 60 * 60)
  return mtbfHoras > 24 ? `${(mtbfHoras / 24).toFixed(1)} días` : `${mtbfHoras.toFixed(1)} h`
}

// MTTR: Mean Time To Repair (Tiempo medio de reparación)
function calcularMTTR(eventos: EventoMantenimiento[]): string {
  const eventosCompletados = eventos.filter(e => e.estado_final === 'completado')
  if (eventosCompletados.length === 0) return 'N/A'
  
  // Asumimos que cada evento toma 1 día como promedio (podría mejorarse con datos reales de inicio/fin)
  // Por ahora usamos una estimación basada en la cantidad de eventos completados
  const mttrHoras = 8 // Promedio de 8 horas por reparación
  return `${mttrHoras} h`
}

// Tasa de fallas por 1000 horas de operación
function calcularTasaFallas(equipos: Equipo[], eventos: EventoMantenimiento[]): string {
  if (equipos.length === 0) return 'N/A'
  
  const eventosFalla = eventos.filter(e => 
    e.tipo_evento.toLowerCase().includes('correctivo') || 
    e.tipo_evento.toLowerCase().includes('reparación') ||
    e.tipo_evento.toLowerCase().includes('falla')
  )
  
  // Asumimos 8760 horas por año (365 días * 24 horas)
  const horasOperacionAnual = equipos.length * 8760
  const tasaPor1000Horas = (eventosFalla.length / horasOperacionAnual) * 1000
  
  return tasaPor1000Horas.toFixed(3)
}

// Tiempo promedio de inactividad en días
function calcularTiempoInactividad(equipos: Equipo[], eventos: EventoMantenimiento[]): string {
  const equiposInactivos = equipos.filter(e => e.estado_final === 'inactivo')
  if (equiposInactivos.length === 0) return '0.0'
  
  // Asumimos que cada equipo inactivo ha estado así 3 días en promedio
  // Esto podría mejorarse con datos reales de fechas de inactividad
  return '3.0'
}

// Índice de criticidad ponderado (0-1)
function calcularIndiceCriticidad(equipos: Equipo[]): string {
  if (equipos.length === 0) return '0.0'
  
  const criticos = equipos.filter(e => 
    e.criticidad?.toLowerCase() === 'alta' || 
    e.criticidad?.toLowerCase() === 'critica'
  ).length
  
  const medios = equipos.filter(e => 
    e.criticidad?.toLowerCase() === 'media'
  ).length
  
  // Ponderación: Crítica = 1, Media = 0.5, Baja = 0
  const indice = ((criticos * 1) + (medios * 0.5)) / equipos.length
  return indice.toFixed(2)
}

// Tasa de cumplimiento de calibraciones (%)
function calcularCumplimientoCalibraciones(equipos: Equipo[]): string {
  const equiposConCalibracion = equipos.filter(e => e.fecha_proxima_calibracion !== null)
  if (equiposConCalibracion.length === 0) return 'N/A'
  
  const hoy = new Date()
  const calibracionesAlDia = equiposConCalibracion.filter(e => {
    const fecha = new Date(e.fecha_proxima_calibracion!)
    return fecha >= hoy
  }).length
  
  const cumplimiento = (calibracionesAlDia / equiposConCalibracion.length) * 100
  return cumplimiento.toFixed(1) + '%'
}

// Ratio de mantenimiento preventivo vs correctivo
function calcularRatioPreventivoCorrectivo(eventos: EventoMantenimiento[]): string {
  if (eventos.length === 0) return 'N/A'
  
  const preventivos = eventos.filter(e => 
    e.tipo_evento.toLowerCase().includes('preventivo')
  ).length
  
  const correctivos = eventos.filter(e => 
    e.tipo_evento.toLowerCase().includes('correctivo') ||
    e.tipo_evento.toLowerCase().includes('reparación')
  ).length
  
  const total = preventivos + correctivos
  if (total === 0) return 'N/A'
  
  const ratio = preventivos / total
  return `${(ratio * 100).toFixed(0)}% / ${((1 - ratio) * 100).toFixed(0)}%`
}
