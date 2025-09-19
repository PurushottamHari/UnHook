import Image from 'next/image';

interface TeerthLogoIconProps {
  className?: string;
  alt?: string;
  priority?: boolean;
  width?: number;
  height?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | number;
}

const sizeClasses = {
  xs: { width: 24, height: 24 },      // 24px square
  sm: { width: 32, height: 32 },      // 32px square
  md: { width: 40, height: 40 },      // 40px square
  lg: { width: 75, height: 50 },      // 48px square
  xl: { width: 56, height: 56 },      // 56px square
  '2xl': { width: 64, height: 64 },   // 64px square
  '3xl': { width: 72, height: 72 },   // 72px square
  '4xl': { width: 80, height: 80 },   // 80px square
  '5xl': { width: 96, height: 96 },   // 96px square
};

export default function TeerthLogoIcon({ 
  className = '', 
  alt = 'Teerth Logo Icon',
  priority = false,
  width,
  height,
  size = 'lg'
}: TeerthLogoIconProps) {
  // Determine dimensions
  let logoWidth: number;
  let logoHeight: number;

  if (width && height) {
    // Use explicit width and height
    logoWidth = width;
    logoHeight = height;
  } else if (width && !height) {
    // Use width as both dimensions (square)
    logoWidth = width;
    logoHeight = width;
  } else if (!width && height) {
    // Use height as both dimensions (square)
    logoWidth = height;
    logoHeight = height;
  } else if (typeof size === 'number') {
    // Use size as both width and height (square)
    logoWidth = size;
    logoHeight = size;
  } else {
    // Use predefined size
    const dimensions = sizeClasses[size];
    logoWidth = dimensions.width;
    logoHeight = dimensions.height;
  }

  return (
    <div 
      className={`relative ${className}`}
      style={{ width: `${logoWidth}px`, height: `${logoHeight}px` }}
    >
      <Image
        src="/assets/logo_without_text.png"
        alt={alt}
        fill
        className="object-none"
        priority={priority}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
    </div>
  );
}
