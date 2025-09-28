import Image from 'next/image';

interface TeerthLogoIconProps {
  className?: string;
  alt?: string;
  priority?: boolean;
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

// Aspect ratio of the logo: 220px width / 135px height ≈ 1.63:1
const LOGO_ASPECT_RATIO = 220 / 135;

// Calculate dimensions from diagonal length
function calculateDimensionsFromDiagonal(diagonal: number) {
  // For a rectangle with aspect ratio a:b, if diagonal = d, then:
  // width = d * a / sqrt(a² + b²)
  // height = d * b / sqrt(a² + b²)
  const a = LOGO_ASPECT_RATIO;
  const b = 1;
  const sqrt = Math.sqrt(a * a + b * b);

  return {
    width: Math.round((diagonal * a) / sqrt),
    height: Math.round((diagonal * b) / sqrt),
  };
}

const sizeClasses = {
  xs: calculateDimensionsFromDiagonal(20), // 20px diagonal
  sm: calculateDimensionsFromDiagonal(30), // 30px diagonal
  md: calculateDimensionsFromDiagonal(40), // 40px diagonal
  lg: calculateDimensionsFromDiagonal(50), // 50px diagonal
  xl: calculateDimensionsFromDiagonal(60), // 60px diagonal
  '2xl': calculateDimensionsFromDiagonal(80), // 80px diagonal
  '3xl': calculateDimensionsFromDiagonal(100), // 100px diagonal
  '4xl': calculateDimensionsFromDiagonal(120), // 120px diagonal
  '5xl': calculateDimensionsFromDiagonal(150), // 150px diagonal
};

export default function TeerthLogoIcon({
  className = '',
  alt = 'Teerth Logo Icon',
  priority = false,
  size = 'lg',
}: TeerthLogoIconProps) {
  // Determine dimensions from diagonal length
  let logoWidth: number;
  let logoHeight: number;

  if (typeof size === 'number') {
    // Use size as diagonal length
    const dimensions = calculateDimensionsFromDiagonal(size);
    logoWidth = dimensions.width;
    logoHeight = dimensions.height;
  } else {
    // Use predefined size
    const dimensions = sizeClasses[size];
    logoWidth = dimensions.width;
    logoHeight = dimensions.height;
  }

  return (
    <div
      className={`relative ${className}`}
      style={{
        width: `${logoWidth}px`,
        height: `${logoHeight}px`,
        display: 'inline-block',
        overflow: 'hidden',
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
  );
}
