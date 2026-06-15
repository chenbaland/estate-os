# EstateOS Design System

**Phase 3 — UI/UX Design System**

A unified design language for web (`frontend/`), mobile (`mobile/`), and future gate-terminal PWA surfaces. Inspired by the clarity of **Apple**, the warmth of **Airbnb**, the motion discipline of **Uber**, the fintech polish of **Revolut**, and the content-first layouts of **Notion**.

---

## Design Principles

| Principle | Description | Reference |
|-----------|-------------|-----------|
| **Clarity over decoration** | Every element earns its place; reduce cognitive load on first use | Apple HIG |
| **Warm professionalism** | Friendly copy, rounded corners, generous whitespace — not cold enterprise UI | Airbnb |
| **Motion with purpose** | Animations communicate state; never block interaction | Uber |
| **Trust through consistency** | Predictable patterns for money, access, and safety flows | Revolut |
| **Content-first layouts** | Modules share a common page scaffold; data density adapts to role | Notion |

---

## Typography

### Font Stack

| Token | Value | Usage |
|-------|-------|-------|
| `--font-sans` | Geist Sans, ui-sans-serif, system-ui | All UI text |
| `--font-mono` | Geist Mono, ui-monospace | QR codes, invoice IDs, API keys |

Geist is loaded in `frontend/src/app/layout.tsx`. Mobile uses system fonts with equivalent scale in `mobile/src/constants/theme.ts`.

### Type Scale

| Name | Size | Line Height | Weight | Usage |
|------|------|-------------|--------|-------|
| `display` | 36px / 2.25rem | 1.1 | 700 | Marketing hero, empty states |
| `h1` | 30px / 1.875rem | 1.2 | 700 | Page titles |
| `h2` | 24px / 1.5rem | 1.25 | 600 | Section headers, card titles |
| `h3` | 20px / 1.25rem | 1.3 | 600 | Sub-sections, dialog titles |
| `h4` | 18px / 1.125rem | 1.4 | 600 | List group headers |
| `body-lg` | 18px | 1.5 | 400 | Lead paragraphs |
| `body` | 16px / 1rem | 1.5 | 400 | Default body text |
| `body-sm` | 14px / 0.875rem | 1.43 | 400 | Secondary text, table cells |
| `caption` | 12px / 0.75rem | 1.33 | 500 | Labels, timestamps, badges |
| `overline` | 11px | 1.2 | 600 | Uppercase section labels (letter-spacing: 0.08em) |

### Typography Rules

- **Page titles** use `h1` with optional `text-balance` utility for multi-line headings.
- **Numeric data** (billing amounts, analytics) use tabular figures where supported.
- **Minimum body size** is 14px on web, 16px on mobile for touch readability.
- **Line length** capped at 65ch for prose blocks (community posts, AI responses).

---

## Color System

Tokens live in `docs/phase-03/tokens.css` and are synced to `frontend/src/styles/tokens.css`.

### Brand Palette

| Token | Light (HSL) | Hex | Usage |
|-------|-------------|-----|-------|
| `--primary` | 262 83% 58% | `#7C3AED` | CTAs, active nav, links |
| `--brand-gradient-from` | 262 83% 58% | — | Hero backgrounds, premium badges |
| `--brand-gradient-to` | 221 83% 53% | `#2563EB` | Gradient end |

Primary violet signals premium estate living; blue gradient accent adds fintech trust (Revolut-inspired).

### Semantic Colors

| Token | Light Hex | Usage |
|-------|-----------|-------|
| `--success` | `#16A34A` | Payment confirmed, gate approved, ticket resolved |
| `--warning` | `#F59E0B` | Pending approvals, expiring passes |
| `--info` | `#0EA5E9` | Informational banners, tooltips |
| `--destructive` | `#EF4444` | SOS, failed payments, blacklist hits |

### Surface Hierarchy

```
background          → page canvas
  card              → elevated panels, stat cards
    popover         → dropdowns, tooltips, command palette
accent / muted      → hover states, secondary actions
border / input      → dividers, form fields
```

### Contrast Requirements (WCAG 2.1 AA)

| Pair | Minimum Ratio | Status |
|------|---------------|--------|
| `foreground` on `background` | 4.5:1 | Pass |
| `primary-foreground` on `primary` | 4.5:1 | Pass |
| `muted-foreground` on `background` | 4.5:1 | Pass (large text 3:1) |
| `destructive-foreground` on `destructive` | 4.5:1 | Pass |

Never use color alone to convey status — pair with icon + text label.

---

## Spacing & Layout

### Spacing Scale (4px base)

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Icon-text gap, tight inline spacing |
| `sm` | 8px | Form field internal padding |
| `md` | 12px | Card padding (mobile) |
| `lg` | 16px | Default card padding, grid gap |
| `xl` | 24px | Section spacing |
| `2xl` | 32px | Page section breaks |
| `3xl` | 48px | Hero / empty state vertical rhythm |

### Layout Constants

| Token | Value | Component |
|-------|-------|-----------|
| `--sidebar-width` | 16rem (256px) | `Sidebar.tsx` |
| `--header-height` | 4rem (64px) | `Header.tsx` |
| `--content-max-width` | 1400px | `.container-app` utility |

### Grid

- **Dashboard**: 12-column responsive grid; stat cards span 3 cols on desktop, 6 on tablet, 12 on mobile.
- **Module pages**: Single-column content with optional right sidebar (480px) for detail panels.
- **Mobile tabs**: Bottom tab bar height 64px (`mobile/src/constants/theme.ts` → `layout.tabBarHeight`).

### Breakpoints (Tailwind defaults)

| Name | Min Width | Behavior |
|------|-----------|----------|
| `sm` | 640px | Collapse sidebar to sheet |
| `md` | 768px | Two-column module layouts |
| `lg` | 1024px | Full sidebar visible |
| `xl` | 1280px | Analytics multi-panel |
| `2xl` | 1536px | Max content width enforced |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 8px | Badges, chips |
| `--radius-md` | 10px | Inputs, buttons |
| `--radius-lg` | 12px | Cards, dialogs (default) |
| `--radius-xl` | 16px | Modals, bottom sheets |
| `full` | 9999px | Avatars, FAB, SOS button |

---

## Elevation & Shadows

| Token | Usage |
|-------|-------|
| `--shadow-sm` | Buttons at rest, input focus ring offset |
| `--shadow-md` | Cards, dropdown menus |
| `--shadow-lg` | Dialogs, floating action areas |
| `--shadow-xl` | Command palette, SOS overlay |

**Glass effect** (`.glass` utility): `bg-background/80 backdrop-blur-xl border border-border/50` — used for sticky headers and notification panels.

---

## Components

Built on **ShadCN UI** + **Radix UI** primitives in `frontend/src/components/ui/`. Mobile equivalents in `mobile/src/components/`.

### Buttons

| Variant | Style | Usage |
|---------|-------|-------|
| `default` | Primary fill | Primary actions (Pay, Create Pass, Send SOS) |
| `secondary` | Muted fill | Cancel, back |
| `outline` | Border only | Tertiary actions |
| `ghost` | No border | Icon buttons, nav items |
| `destructive` | Red fill | Delete, revoke pass |
| `link` | Text + underline | Inline navigation |

**Sizes**: `sm` (32px), `default` (40px), `lg` (48px), `icon` (40×40).

Minimum touch target: **44×44px** on mobile (Uber guideline).

### Form Controls

- **Input**: 40px height, `--radius-md`, focus ring `--ring`.
- **Select / Dropdown**: Radix-powered; keyboard navigable.
- **Checkbox / Switch**: Used for preferences, feature toggles.
- **Form validation**: Zod + react-hook-form; inline error text in `--destructive`.

### Cards

```tsx
<Card>
  <CardHeader>
    <CardTitle>Outstanding Balance</CardTitle>
    <CardDescription>Due March 15, 2026</CardDescription>
  </CardHeader>
  <CardContent>...</CardContent>
  <CardFooter>...</CardFooter>
</Card>
```

Stat cards on dashboard use compact variant with icon badge in `--accent` background.

### Navigation

| Surface | Component | Path |
|---------|-----------|------|
| Web sidebar | `Sidebar.tsx` | Role-filtered via `navigation.ts` |
| Web header | `Header.tsx` | Estate switcher, theme toggle, notifications |
| Mobile bottom tabs | `TabBar.tsx` | Home, Visitors, Community, Marketplace, Profile |
| Mobile stack | Expo Router | Push transitions for detail screens |

### Data Display

- **Table**: Sortable columns, row hover, sticky header on scroll.
- **Badge**: Status chips (`success`, `warning`, `destructive`, `secondary`).
- **Avatar**: User/resident photos with initials fallback.
- **Chart**: Recharts with token-aligned colors (`chart.tsx`).

### Feedback

- **Toast** (Sonner): Success/error/info; bottom-right on desktop, top on mobile.
- **Dialog / Sheet**: Confirmations, multi-step forms.
- **Skeleton**: Loading placeholders matching content shape.

### Module Page Scaffold

All dashboard modules use `ModulePage.tsx`:

```
┌─────────────────────────────────────────┐
│ Page title + description + actions      │
├─────────────────────────────────────────┤
│ Filters / tabs (optional)               │
├─────────────────────────────────────────┤
│ Main content (table, grid, or form)     │
└─────────────────────────────────────────┘
```

---

## Animation Standards

Powered by **Framer Motion** on web, **Reanimated** on mobile.

### Timing

| Type | Duration | Easing | Usage |
|------|----------|--------|-------|
| Micro | 100–150ms | `ease-out` | Hover, focus, toggle |
| Standard | 200–250ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Page transitions, sheet open |
| Emphasis | 300–400ms | `spring(damping: 20)` | SOS pulse, success checkmark |
| Stagger | 50ms delay/item | — | List entrance, dashboard widgets |

### Motion Patterns

| Pattern | Spec |
|---------|------|
| Page enter | Fade + translateY(8px) → 0 |
| Sheet / drawer | Slide from edge, backdrop fade 200ms |
| Modal | Scale 0.95 → 1 + fade |
| List item | Stagger fade-in on mount |
| SOS button | Continuous pulse ring (destructive color) |
| QR reveal | Scale spring on pass generation |

### Reduced Motion

Respect `prefers-reduced-motion: reduce` — disable non-essential animations, keep instant state changes.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Dark / Light Mode

Implemented via `next-themes` (`frontend/src/components/providers/theme-provider.tsx`).

| Aspect | Light | Dark |
|--------|-------|------|
| Background | White `#FFFFFF` | Near-black `#09090B` |
| Cards | White | Elevated `#18181B` |
| Primary | Violet 600 | Violet 500 (slightly brighter) |
| Borders | Zinc 200 | Zinc 800 |

- **Default**: System preference (`prefers-color-scheme`).
- **Toggle**: Header sun/moon icon; persisted in `localStorage`.
- **Mobile**: Follows system via `expo-system-ui`; manual override in Profile → Appearance.
- **Images**: Slight opacity reduction in dark mode for photo cards.

---

## Accessibility (WCAG 2.1 AA)

### Keyboard

- All interactive elements reachable via Tab.
- Focus visible: `ring-2 ring-ring ring-offset-2` (see `globals.css`).
- Escape closes dialogs, sheets, dropdowns.
- Skip link to main content on web layouts.

### Screen Readers

- Semantic HTML: `<nav>`, `<main>`, `<header>`, `<article>`.
- `aria-label` on icon-only buttons.
- Live regions for toast notifications and SOS status updates.
- Form fields linked via `<Label htmlFor>`.

### Color & Contrast

- All text meets 4.5:1 contrast (see Color System table).
- Focus indicators meet 3:1 against adjacent colors.
- Status badges include text labels, not color-only dots.

### Touch & Motor

- 44px minimum touch targets on mobile.
- Adequate spacing between destructive actions (confirm dialog required).
- SOS requires long-press (500ms) to prevent accidental triggers.

### Internationalization Ready

- Layout supports RTL mirroring (future).
- Date/number formatting via `Intl` APIs.
- No text baked into images.

---

## Iconography

**Lucide React** on web, **@expo/vector-icons** (Ionicons) on mobile.

| Context | Size | Stroke |
|---------|------|--------|
| Nav item | 20px | 1.5 |
| Inline / button | 16px | 2 |
| Empty state | 48px | 1.5 |
| SOS | 28px | 2.5 |

Icons always paired with text labels in navigation; standalone icons require `aria-label`.

---

## White-Label (Enterprise Tier)

Estates on the enterprise plan can override tokens per tenant:

```css
[data-estate-theme="lagos-heights"] {
  --primary: 210 100% 45%;
  --brand-gradient-from: 210 100% 45%;
  --brand-gradient-to: 180 70% 40%;
}
```

Overrides injected via `estate-store` theme config; mobile reads equivalent from API `/api/v1/estates/{id}/theme/`.

---

## File Reference

| Asset | Path |
|-------|------|
| CSS tokens (canonical) | `docs/phase-03/tokens.css` |
| CSS tokens (web) | `frontend/src/styles/tokens.css` |
| Global styles | `frontend/src/app/globals.css` |
| UI components | `frontend/src/components/ui/` |
| Layout shell | `frontend/src/components/layout/` |
| Mobile theme | `mobile/src/constants/theme.ts` |
| Navigation config | `frontend/src/lib/navigation.ts` |

---

## Related Documentation

- [Wireframes](./wireframes.md)
- [Screen Specifications](./screens.md)
- [Design Tokens (CSS)](./tokens.css)
- [Phase 5 — Frontend Implementation](../phase-05/README.md)
