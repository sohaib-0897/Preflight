# Interface architecture

The maintained interface is Next.js App Router with React, strict TypeScript, locally packaged Inter/JetBrains Mono, Tailwind tokens, Radix dialogs, TanStack Query, React Hook Form and Zod. Server route shells load the client application; authenticated API queries use scoped cache keys and invalidate after writes. The compatibility TypeScript/FastAPI interface remains available.

The design uses monochrome surfaces, subtle borders, readable controls and semantic status colors. Main navigation connects organizations, projects, agents/versions, evaluations, benchmarks, RealityCheck, security, traces, comparisons, gates, reports and settings. Empty states and onboarding use actual scoped records; no live activity is fabricated. Run pagination and status filters are server-backed; other search explicitly applies to loaded records.

Desktop/mobile Chromium journeys execute account/project/agent/evaluation, configured RealityCheck/review, security and comparison workflows. Axe checks, focus restoration, keyboard table scrolling and export tests supplement actual screenshot reviews. Tables have captions and focusable scroll regions; dialogs restore focus; skip navigation is visible on focus. These checks support WCAG 2.2 AA-oriented development but do not establish complete conformance or assistive-technology coverage.

Design references: [Vercel Geist](https://vercel.com/geist/stack), [Linear navigation](https://linear.app/now/how-we-redesigned-the-linear-ui), [GitHub Primer](https://primer.github.io/), [Grafana Saga](https://grafana.com/developers/saga/) and [Carbon tables](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/accessibility). These informed principles, not copied layouts.
