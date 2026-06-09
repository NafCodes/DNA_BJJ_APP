'use client'

import {
  type FC,
  type ReactNode,
  useRef,
  useEffect,
  useState,
} from 'react'
import {
  motion,
  AnimatePresence,
  useScroll,
  useTransform,
  useMotionValue,
  useInView,
  useMotionValueEvent,
  animate,
  LayoutGroup,
} from 'framer-motion'

// ── Page transition ───────────────────────────────────────────────────────────
// Wrap each page's root element with this.
// AnimatePresence must exist in app/layout.tsx (see SKILL.md Step 6).

interface PageTransitionProps {
  children: ReactNode
  className?: string
}

export const PageTransition: FC<PageTransitionProps> = ({
  children,
  className,
}) => (
  <motion.div
    className={className}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] } }}
    exit={{ opacity: 0, y: -10, transition: { duration: 0.2 } }}
  >
    {children}
  </motion.div>
)

// ── Stagger container + item ──────────────────────────────────────────────────
// Usage:
//   <StaggerContainer className="grid grid-cols-3 gap-4">
//     {items.map(item => (
//       <StaggerItem key={item.id}><Card {...item} /></StaggerItem>
//     ))}
//   </StaggerContainer>

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08, delayChildren: 0.15 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring' as const, stiffness: 300, damping: 30 },
  },
}

interface StaggerContainerProps {
  children: ReactNode
  className?: string
}

export const StaggerContainer: FC<StaggerContainerProps> = ({
  children,
  className,
}) => (
  <motion.div
    className={className}
    variants={containerVariants}
    initial="hidden"
    animate="show"
  >
    {children}
  </motion.div>
)

interface StaggerItemProps {
  children: ReactNode
  className?: string
}

export const StaggerItem: FC<StaggerItemProps> = ({ children, className }) => (
  <motion.div className={className} variants={itemVariants}>
    {children}
  </motion.div>
)

// ── Scroll reveal ─────────────────────────────────────────────────────────────
// Fires once when scrolled into view. Use for section content reveals.

interface RevealOnScrollProps {
  children: ReactNode
  className?: string
  delay?: number
}

export const RevealOnScroll: FC<RevealOnScrollProps> = ({
  children,
  className,
  delay = 0,
}) => {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: '-80px' })

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 40 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.25, 0.1, 0.25, 1] }}
    >
      {children}
    </motion.div>
  )
}

// ── Parallax hero ─────────────────────────────────────────────────────────────
// `bg` renders at parallax speed (e.g. a Canvas or background image).
// `children` render at normal scroll speed (foreground content).

interface ParallaxHeroProps {
  children: ReactNode
  bg: ReactNode
  className?: string
}

export const ParallaxHero: FC<ParallaxHeroProps> = ({
  children,
  bg,
  className = 'relative h-screen overflow-hidden',
}) => {
  const ref = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start start', 'end start'],
  })
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '30%'])
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0])

  return (
    <section ref={ref} className={className}>
      <motion.div style={{ y, opacity }} className="absolute inset-0">
        {bg}
      </motion.div>
      <div className="relative z-10 flex h-full items-center justify-center">
        {children}
      </div>
    </section>
  )
}

// ── Animated modal ────────────────────────────────────────────────────────────
// Spring-physics open/close with backdrop. Traps focus on open.
// Replace any display:none / hidden class toggling with this.

interface AnimatedModalProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
  className?: string
}

export const AnimatedModal: FC<AnimatedModalProps> = ({
  isOpen,
  onClose,
  children,
  className = 'fixed left-1/2 top-1/2 z-50 w-full max-w-lg bg-background rounded-2xl p-6 shadow-2xl',
}) => {
  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isOpen) return
    const panel = panelRef.current
    if (!panel) return

    // Focus the first focusable element when opening
    const focusable = panel.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    )
    focusable[0]?.focus()

    // Trap focus within the modal
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { onClose(); return }
      if (e.key !== 'Tab') return
      const els = Array.from(focusable)
      if (els.length === 0) return
      const first = els[0]
      const last = els[els.length - 1]
      if (e.shiftKey) {
        if (document.activeElement === first) { e.preventDefault(); last.focus() }
      } else {
        if (document.activeElement === last) { e.preventDefault(); first.focus() }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            aria-hidden="true"
          />
          <motion.div
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            className={className}
            style={{ x: '-50%', y: '-50%' }}
            initial={{ opacity: 0, scale: 0.92, x: '-50%', y: '-45%' }}
            animate={{ opacity: 1, scale: 1, x: '-50%', y: '-50%' }}
            exit={{ opacity: 0, scale: 0.95, x: '-50%', y: '-47%' }}
            transition={{ type: 'spring', stiffness: 400, damping: 35 }}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// ── Drawer ────────────────────────────────────────────────────────────────────
// Side panel — slides in from the right.

interface DrawerProps {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
  width?: string
}

export const Drawer: FC<DrawerProps> = ({
  isOpen,
  onClose,
  children,
  width = 'w-80',
}) => (
  <AnimatePresence>
    {isOpen && (
      <>
        <motion.div
          className="fixed inset-0 z-40 bg-black/40"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          aria-hidden="true"
        />
        <motion.aside
          className={`fixed right-0 top-0 z-50 h-full ${width} overflow-y-auto bg-background p-6 shadow-2xl`}
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', stiffness: 400, damping: 40 }}
        >
          {children}
        </motion.aside>
      </>
    )}
  </AnimatePresence>
)

// ── Hover card ────────────────────────────────────────────────────────────────

interface HoverCardProps {
  children: ReactNode
  className?: string
}

export const HoverCard: FC<HoverCardProps> = ({ children, className }) => (
  <motion.div
    className={className}
    whileHover={{ scale: 1.02, y: -4 }}
    whileTap={{ scale: 0.98 }}
    transition={{ type: 'spring', stiffness: 300, damping: 25 }}
  >
    {children}
  </motion.div>
)

// ── Animated button ───────────────────────────────────────────────────────────

interface AnimatedButtonProps {
  children: ReactNode
  onClick?: () => void
  className?: string
  type?: 'button' | 'submit' | 'reset'
  disabled?: boolean
}

export const AnimatedButton: FC<AnimatedButtonProps> = ({
  children,
  onClick,
  className,
  type = 'button',
  disabled = false,
}) => (
  <motion.button
    type={type}
    className={className}
    onClick={onClick}
    disabled={disabled}
    whileHover={disabled ? {} : { scale: 1.04, y: -2 }}
    whileTap={disabled ? {} : { scale: 0.97 }}
    transition={{ type: 'spring', stiffness: 400, damping: 20 }}
  >
    {children}
  </motion.button>
)

// ── Animated counter ──────────────────────────────────────────────────────────
// Counts from `from` to `to` on mount. Wrap with RevealOnScroll to trigger on scroll.

interface AnimatedCounterProps {
  from?: number
  to: number
  duration?: number
  suffix?: string
  prefix?: string
}

export const AnimatedCounter: FC<AnimatedCounterProps> = ({
  from = 0,
  to,
  duration = 1.5,
  suffix = '',
  prefix = '',
}) => {
  const count = useMotionValue(from)
  const [display, setDisplay] = useState(from)

  useEffect(() => {
    const controls = animate(count, to, {
      duration,
      ease: 'easeOut',
      onUpdate: (v) => setDisplay(Math.round(v)),
    })
    return controls.stop
  }, [to, duration, count])

  return (
    <span>
      {prefix}
      {display.toLocaleString()}
      {suffix}
    </span>
  )
}

// ── Animated tabs with layoutId underline ─────────────────────────────────────
// Zero manual position calculations — layoutId handles the morph.

interface Tab {
  id: string
  label: string
}

interface AnimatedTabsProps {
  tabs: Tab[]
  activeTab: string
  onTabChange: (id: string) => void
  className?: string
}

export const AnimatedTabs: FC<AnimatedTabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className = 'flex gap-6 border-b border-border',
}) => (
  <LayoutGroup>
    <nav className={className}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          onClick={() => onTabChange(tab.id)}
          className="relative pb-2 text-sm font-medium transition-colors hover:text-foreground"
        >
          {tab.label}
          {activeTab === tab.id && (
            <motion.div
              layoutId="tab-indicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
            />
          )}
        </button>
      ))}
    </nav>
  </LayoutGroup>
)

// ── Scroll progress bar ───────────────────────────────────────────────────────
// Fixed top bar showing page scroll depth. Common on long-form pages.
// Add once to the root layout.

interface ScrollProgressProps {
  color?: string
  height?: number
  zIndex?: number
}

export const ScrollProgress: FC<ScrollProgressProps> = ({
  color = 'var(--color-primary, #7c3aed)',
  height = 3,
  zIndex = 100,
}) => {
  const { scrollYProgress } = useScroll()

  return (
    <motion.div
      style={{
        scaleX: scrollYProgress,
        transformOrigin: 'left',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height,
        background: color,
        zIndex,
      }}
    />
  )
}

// ── Loading screen ────────────────────────────────────────────────────────────
// Full-screen overlay that exits when isLoading flips to false.
// Add near the root of your app — wraps content while data loads.

interface LoadingScreenProps {
  isLoading: boolean
  children?: ReactNode
  backgroundColor?: string
}

export const LoadingScreen: FC<LoadingScreenProps> = ({
  isLoading,
  children,
  backgroundColor = 'var(--color-background, #0f0f0f)',
}) => (
  <AnimatePresence>
    {isLoading && (
      <motion.div
        role="status"
        aria-label="Loading"
        style={{ backgroundColor }}
        className="fixed inset-0 z-[200] flex items-center justify-center"
        initial={{ opacity: 1 }}
        exit={{ opacity: 0, transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] } }}
      >
        {children ?? (
          <motion.div
            className="h-8 w-8 rounded-full border-2 border-primary border-t-transparent"
            animate={{ rotate: 360 }}
            transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
          />
        )}
      </motion.div>
    )}
  </AnimatePresence>
)

// ── Spring physics reference ───────────────────────────────────────────────────
//
//   Use case          stiffness  damping
//   ─────────────────────────────────────
//   Snappy button        400       20
//   Modal open           400       35
//   Page transition      300       30
//   Floating / slow      150       20
//   Draggable            500       50
//
//   Duration-based easing:
//   ease: [0.25, 0.1, 0.25, 1]  → standard material
//   ease: [0.4, 0, 0.2, 1]      → decelerate-in (entering elements)
//   ease: [0, 0, 0.2, 1]        → accelerate-out (exiting elements)
