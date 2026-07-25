'use client';

interface WelcomeHeaderProps {
  userName?: string | null;
  isAdmin: boolean;
  establishmentName?: string | null;
}

/**
 * WelcomeHeader - Header de bienvenida personalizado
 */
export function WelcomeHeader({ userName, isAdmin, establishmentName }: WelcomeHeaderProps) {
  return (
    <div>
      <h1 className="text-2xl font-bold">
        Bienvenido{userName ? `, ${userName}` : ''}
      </h1>
      <p className="text-sm text-[var(--muted)] mt-1">
        {isAdmin
          ? 'Panel de administración — gestión completa del sistema'
          : `Vista de su establecimiento: ${establishmentName || '...'}`}
      </p>
    </div>
  );
}

export default WelcomeHeader;
