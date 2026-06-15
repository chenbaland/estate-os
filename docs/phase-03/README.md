# Phase 3 — UI/UX Design System

## Deliverables

| Document | Description |
|----------|-------------|
| [design-system.md](./design-system.md) | Complete design system specification |
| [wireframes.md](./wireframes.md) | Wireframe documentation for key flows |
| [screens.md](./screens.md) | High-fidelity screen specifications |
| [tokens.css](./tokens.css) | Design tokens (CSS custom properties) |

## Implementation

Design tokens implemented in:
- `frontend/src/styles/tokens.css`
- `frontend/src/components/ui/` (ShadCN component library)
- `mobile/src/constants/theme.ts`

## Implementation Rationale

A unified design system ensures consistency across web, mobile, and future gate terminal PWA. Tokens enable instant dark/light mode switching and white-label customization per estate (enterprise tier).

## Deployment

Documentation + frontend/mobile token implementation. Preview design system:

```bash
cd frontend && npm run dev
# Visit http://localhost:3000
```
