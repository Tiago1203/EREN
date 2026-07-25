'use client';

import { useState } from 'react';
import { getSignedUrlForPath } from '@/lib/storage';
import type { Establishment } from '../types/dashboard.types';

interface EstablishmentInfoProps {
  establishment: Establishment;
}

/**
 * EstablishmentInfo - Información del establecimiento
 */
export function EstablishmentInfo({ establishment }: EstablishmentInfoProps) {
  const [loadingCert, setLoadingCert] = useState(false);

  const handleViewCert = async () => {
    if (!establishment.url_certificado_acess) return;
    
    setLoadingCert(true);
    try {
      const { signedURL, error } = await getSignedUrlForPath(
        ['certificados', 'manuales'],
        establishment.url_certificado_acess,
        300
      );
      if (error || !signedURL) {
        alert('No se puede obtener el certificado. Revisa permisos.');
        return;
      }
      window.open(signedURL, '_blank');
    } finally {
      setLoadingCert(false);
    }
  };

  const infoItems = [
    ['RUC', establishment.ruc],
    ['Nombre Comercial', establishment.nombre_comercial],
    ['Tipología', establishment.tipologia],
    ['Responsable Técnico', establishment.responsable_tecnico_cedula],
    ...(establishment.direccion ? [['Dirección', establishment.direccion]] : []),
  ];

  return (
    <div className="card p-6">
      <h3 className="text-base font-semibold mb-4">Mi Establecimiento</h3>
      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        {infoItems.map(([label, value]) => (
          <div key={label as string}>
            <dt className="text-[var(--muted)]">{label}</dt>
            <dd className="font-medium mt-0.5">{value}</dd>
          </div>
        ))}
      </dl>
      
      {establishment.url_certificado_acess && (
        <div className="mt-4">
          <button
            className="btn-secondary text-sm"
            onClick={handleViewCert}
            disabled={loadingCert}
          >
            {loadingCert ? 'Cargando...' : 'Ver certificado'}
          </button>
        </div>
      )}
    </div>
  );
}

export default EstablishmentInfo;
