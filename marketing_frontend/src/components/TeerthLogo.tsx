import Image from 'next/image';

interface TeerthLogoProps {
  className?: string;
  alt?: string;
  priority?: boolean;
  width?: number;
  height?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl' | number;
}

const sizeClasses = {
  xs: { width: 32, height: 24 },      // 4:3 ratio
  sm: { width: 48, height: 36 },      // 4:3 ratio
  md: { width: 64, height: 48 },      // 4:3 ratio
  lg: { width: 80, height: 60 },      // 4:3 ratio
  xl: { width: 96, height: 72 },      // 4:3 ratio
  '2xl': { width: 128, height: 96 },  // 4:3 ratio
  '3xl': { width: 160, height: 120 }, // 4:3 ratio
  '4xl': { width: 192, height: 144 }, // 4:3 ratio
  '5xl': { width: 224, height: 168 }, // 4:3 ratio
};

export default function TeerthLogo({ 
  className = '', 
  alt = 'Teerth Logo',
  priority = false,
  width,
  height,
  size = 'lg'
}: TeerthLogoProps) {
  // Determine dimensions
  let logoWidth: number;
  let logoHeight: number;

  if (width && height) {
    // Use explicit width and height
    logoWidth = width;
    logoHeight = height;
  } else if (typeof size === 'number') {
    // Use size as width, calculate height maintaining aspect ratio
    logoWidth = size;
    logoHeight = size * 0.75; // Assuming 4:3 aspect ratio
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
        src="/assets/TeerthLogo.png"
        alt={alt}
        fill
        className="object-none"
        priority={priority}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      />
    </div>
  );
}
