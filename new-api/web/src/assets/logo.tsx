/*
Copyright (C) 2023-2026 QuantumNous

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

For commercial licensing, please contact support@quantumnous.com
*/
import { type SVGProps } from 'react'

import { cn } from '@/lib/utils'

export function Logo({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg
      id='daikon-logo'
      viewBox='0 0 24 24'
      xmlns='http://www.w3.org/2000/svg'
      height='24'
      width='24'
      fill='none'
      stroke='currentColor'
      strokeWidth='1.75'
      strokeLinecap='round'
      strokeLinejoin='round'
      className={cn('size-6', className)}
      {...props}
    >
      <title>Daikon API</title>
      {/* Leaves */}
      <path
        d='M12 7.5C12 4.5 13 2 15 2C15 4.5 13.8 6.5 12 7.5Z'
        className='fill-primary stroke-primary'
      />
      <path
        d='M11.5 7.5C10 5 8 3.5 6 4C6.5 6 8.5 7.5 11.5 7.5Z'
        className='fill-primary/80 stroke-primary'
      />
      <path
        d='M12.5 7.5C14 5.5 16.5 4.5 18 5.5C17.5 7.2 15 8 12.5 7.5Z'
        className='fill-primary/80 stroke-primary'
      />
      {/* Daikon Radish Root Body */}
      <path
        d='M8 8C7.5 12 9 17 11.5 22C11.7 22.4 12.3 22.4 12.5 22C15 17 16.5 12 16 8C16 7.2 15 6.5 12 6.5C9 6.5 8 7.2 8 8Z'
        className='fill-background stroke-foreground'
      />
      {/* Root subtle texture lines */}
      <path d='M10 11.5H13' className='stroke-muted-foreground/60' />
      <path d='M11 15H14' className='stroke-muted-foreground/60' />
      <path d='M11 18.5H13' className='stroke-muted-foreground/60' />
    </svg>
  )
}
