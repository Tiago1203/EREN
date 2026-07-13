import React, { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { getSignedUrlForPath, removeFileFromBucket } from '@/lib/storage'
import { supabase } from '@/lib/supabase'

export function FileViewer({
  path,
  establecimientoId,
  onDeleted,
}: {
  path: string | null
  establecimientoId: number
  onDeleted?: () => void
}) {
  const { profile, isAdmin } = useAuth()
  const [url, setUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      if (!path) return
      // solo admin o usuario del establecimiento pueden obtener URL
      if (!isAdmin && profile?.establecimiento_id !== establecimientoId) return
      setLoading(true)
      const { signedURL, error } = await getSignedUrlForPath(['certificados', 'informes', 'manuales'], path, 300)
      if (!mounted) return
      if (!error && signedURL) setUrl(signedURL)
      setLoading(false)
    }
    load()
    return () => { mounted = false }
  }, [path, isAdmin, profile, establecimientoId])

  const handleDelete = async () => {
    if (!isAdmin) return
    if (!path) return
    if (!confirm('Eliminar archivo permanentemente?')) return
    const { error } = await removeFileFromBucket(['certificados', 'informes', 'manuales'], path)
    if (error) {
      alert('Error al eliminar archivo: ' + (error.message || JSON.stringify(error)))
      return
    }
    // update possible DB refs: try both tablas
    await supabase.from('equipos').update({ url_manual_tecnico: null }).eq('url_manual_tecnico', path)
    await supabase.from('establecimientos').update({ url_certificado_acess: null }).eq('url_certificado_acess', path)
    onDeleted && onDeleted()
  }

  if (!path) return <span>—</span>
  if (!isAdmin && profile?.establecimiento_id !== establecimientoId) return <span>Archivo (sin acceso)</span>
  if (loading) return <span>Cargando...</span>
  if (!url) return <span>No disponible</span>

  const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(path)

  return (
    <div className="flex items-center gap-3">
      {isImage ? (
        <img src={url} alt="preview" className="w-20 h-14 object-contain rounded" />
      ) : (
        <svg className="w-6 h-6 text-[var(--muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v12"/><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-6"/></svg>
      )}
      <div className="flex flex-col">
        <a href={url} target="_blank" rel="noreferrer" className="text-[var(--primary)] hover:underline">Abrir</a>
        {isAdmin && (
          <button onClick={handleDelete} className="text-xs text-[var(--danger)] hover:underline mt-1">Eliminar</button>
        )}
      </div>
    </div>
  )
}

export default FileViewer
