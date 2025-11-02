import Image from 'next/image';

interface TeerthLogoProps {
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

// Aspect ratio of the full Teerth logo: 790px width / 135px height ≈ 5.85:1
const TEERTH_LOGO_ASPECT_RATIO = 165 / 45;

// Calculate dimensions from diagonal length
function calculateDimensionsFromDiagonal(diagonal: number) {
  // For a rectangle with aspect ratio a:b, if diagonal = d, then:
  // width = d * a / sqrt(a² + b²)
  // height = d * b / sqrt(a² + b²)
  const a = TEERTH_LOGO_ASPECT_RATIO;
  const b = 1;
  const sqrt = Math.sqrt(a * a + b * b);

  return {
    width: Math.round((diagonal * a) / sqrt),
    height: Math.round((diagonal * b) / sqrt),
  };
}

const sizeClasses = {
  xs: calculateDimensionsFromDiagonal(30), // 30px diagonal
  sm: calculateDimensionsFromDiagonal(50), // 50px diagonal
  md: calculateDimensionsFromDiagonal(70), // 70px diagonal
  lg: calculateDimensionsFromDiagonal(90), // 90px diagonal
  xl: calculateDimensionsFromDiagonal(110), // 110px diagonal
  '2xl': calculateDimensionsFromDiagonal(150), // 150px diagonal
  '3xl': calculateDimensionsFromDiagonal(200), // 200px diagonal
  '4xl': calculateDimensionsFromDiagonal(250), // 250px diagonal
  '5xl': calculateDimensionsFromDiagonal(300), // 300px diagonal
};

export default function TeerthLogo({
  className = '',
  alt = 'Teerth Logo',
  priority = false,
  size = 'lg',
}: TeerthLogoProps) {
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
        src='/assets/TeerthLogo.png'
        alt={alt}
        fill
        className='object-contain'
        priority={priority}
        sizes='(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw'
      />
    </div>
  );
}
