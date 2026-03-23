import Image from 'next/image';

interface TeerthLogoProps {
  className?: string;
  alt?: string;
  priority?: boolean;
  useIconOnMobile?: boolean;
  size?:
    | 'xs'
    | 'sm'
    | 'md'
    | 'lg'
    | 'xl'
    | '2xl'
    | '3xl'
    | '4xl'
    | '5xl'
    | number;
}

// Aspect ratio of the full Teerth logo: 165px width / 45px height ≈ 3.67:1
const TEERTH_LOGO_ASPECT_RATIO = 165 / 45;

// Aspect ratio of the icon only logo: 220px width / 135px height ≈ 1.63:1
const ICON_LOGO_ASPECT_RATIO = 220 / 135;

// Calculate dimensions from diagonal length
function calculateDimensionsFromDiagonal(diagonal: number, aspectRatio: number) {
  const a = aspectRatio;
  const b = 1;
  const sqrt = Math.sqrt(a * a + b * b);

  return {
    width: Math.round((diagonal * a) / sqrt),
    height: Math.round((diagonal * b) / sqrt),
  };
}

const sizeClasses = {
  xs: 30,
  sm: 50,
  md: 70,
  lg: 90,
  xl: 110,
  '2xl': 150,
  '3xl': 200,
  '4xl': 250,
  '5xl': 300,
};

export default function TeerthLogo({
  className = '',
  alt = 'Teerth Logo',
  priority = false,
  useIconOnMobile = false,
  size = 'lg',
}: TeerthLogoProps) {
  const diagonal = typeof size === 'number' ? size : sizeClasses[size];
  
  const fullDimensions = calculateDimensionsFromDiagonal(diagonal, TEERTH_LOGO_ASPECT_RATIO);
  const iconDimensions = calculateDimensionsFromDiagonal(diagonal * 0.75, ICON_LOGO_ASPECT_RATIO); // Slightly smaller icon

  return (
    <div className={`relative ${className} inline-flex items-center justify-center`}>
      {/* Full Logo - Hidden on mobile if useIconOnMobile is true */}
      <div
        className={`${useIconOnMobile ? 'hidden md:block' : 'block'} relative`}
        style={{
          width: `${fullDimensions.width}px`,
          height: `${fullDimensions.height}px`,
        }}
      >
        <Image
          src='/assets/TeerthLogo.png'
          alt={alt}
          fill
          className='object-contain'
          priority={priority}
          sizes='(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw'
        />
      </div>

      {/* Icon Logo - Shown only on mobile if useIconOnMobile is true */}
      {useIconOnMobile && (
        <div
          className='md:hidden relative'
          style={{
            width: `${iconDimensions.width}px`,
            height: `${iconDimensions.height}px`,
          }}
        >
          <Image
            src='/assets/logo_without_text.png'
            alt={alt}
            fill
            className='object-contain'
            priority={priority}
            sizes='(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw'
          />
        </div>
      )}
    </div>
  );
}
