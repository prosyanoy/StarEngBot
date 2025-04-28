const defaultTheme = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ['class'],
    content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
  	extend: {
		  rotate:{ 'y-180':'180deg' },
		fontFamily: {
        	sans: ['var(--font-roboto)', ...defaultTheme.fontFamily.sans],
        	mono: ['var(--font-roboto-mono)', ...defaultTheme.fontFamily.mono],
      	},
  		borderRadius: {
  			card: '1.5rem',
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		colors: {
			  'telegram-white': 'var(--telegram-bg-color)',
				'telegram-black': 'var(--telegram-text-color)',
        		'telegram-hint': 'var(--telegram-hint-color)',
        		'telegram-link': 'var(--telegram-link-color)',
        		'telegram-primary': 'var(--telegram-button-color)',
        		'telegram-primary-text': 'var(--telegram-button-text-color)',
        		'telegram-secondary-white': 'var(--telegram-secondary-bg-color)',
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		}
  	}
  },
  plugins: [
	  require("tailwindcss-animate"),
	  function ({ addUtilities }) {
      addUtilities({
        '.[transform-style\\:preserve-3d]': {
          transformStyle: 'preserve-3d',
        },
        '.[backface-visibility\\:hidden]': {
          backfaceVisibility: 'hidden',
        },
        '.rotate-y-180': {
          transform: 'rotateY(180deg)',
        },
      });
    }
	]
}

