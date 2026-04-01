import React from 'react'

type Variant = 'primary' | 'ghost' | 'outline'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  children: React.ReactNode
  fullWidth?: boolean
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-gray-900 text-white hover:bg-gray-700 active:bg-gray-800 focus-visible:ring-gray-900',
  ghost:
    'bg-transparent text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus-visible:ring-gray-400',
  outline:
    'bg-transparent border border-gray-300 text-gray-700 hover:border-gray-900 hover:text-gray-900 focus-visible:ring-gray-400',
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-5 py-2 text-sm',
  lg: 'px-6 py-2.5 text-base',
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  fullWidth = false,
  className = '',
  ...props
}) => {
  return (
    <button
      className={[
        'inline-flex items-center justify-center gap-2 rounded-full font-medium',
        'transition-all duration-150 ease-in-out',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variantClasses[variant],
        sizeClasses[size],
        fullWidth ? 'w-full' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
      {...props}
    >
      {children}
    </button>
  )
}
