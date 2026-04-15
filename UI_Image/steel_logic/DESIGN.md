# Design System Specification: Industrial Intelligence

## 1. Overview & Creative North Star
**Creative North Star: "The Precision Architect"**

This design system moves beyond basic utility to embody the spirit of high-end industrial automation. It is inspired by the intersection of heavy machinery and predictive intelligence. Unlike generic SaaS platforms that feel airy and abstract, this system feels grounded, structural, and hyper-organized. 

We break the "template" look by utilizing **intentional asymmetry** and **tonal layering**. We treat the interface not as a flat screen, but as a high-performance dashboard where information is weighted by importance. Expect tight, purposeful spacing (Compact Industrialism) balanced against expansive, bold typography that mirrors the authoritative nature of AI-driven logistics.

---

## 2. Colors: Tonal Architecture
The palette is rooted in deep structural blues and atmospheric grays. We move away from stark blacks and whites to create a more sophisticated, "low-strain" environment for professional users.

### The Palette
*   **Primary (Action):** `#0058be` — Used for critical interaction points.
*   **Surface (Sidebar):** `#171c1f` (On-Surface) / `#1f2a37` (Contextual) — Provides a solid anchor to the application.
*   **Neutral (Background):** `#f6fafd` — A crisp, cool-toned base.
*   **Status Indicators:** `tertiary` (#006947) for "Optimal," `error` (#ba1a1a) for "Critical Interruption."

### The "No-Line" Rule
**Borders are an admission of failure in hierarchy.** This system prohibits the use of 1px solid borders to section content. Boundaries must be defined through:
1.  **Background Shifts:** Transitioning from `surface` to `surface-container-low`.
2.  **Tonal Transitions:** Using `surface-container-highest` to define a header area against a `surface-container` body.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. Use the following tiers to define depth:
*   **Base:** `surface` (#f6fafd)
*   **Lower Level (Sections):** `surface-container-low` (#f0f4f7)
*   **Card Level:** `surface-container-lowest` (#ffffff) — The "highest" physical point for content.
*   **Interaction Level:** `surface-container-high` (#e5e9ec) — For hover states and active selections.

### The "Glass & Gradient" Rule
To inject visual "soul," use subtle gradients on primary CTAs (transitioning from `primary` to `primary-container`). For floating modals or "always-on" status overlays, utilize **Glassmorphism**: `surface-container-lowest` at 80% opacity with a `20px` backdrop-blur to keep the user grounded in their current context.

---

## 3. Typography: Authoritative Inter
We use **Inter** exclusively to lean into its technical, legible character. The hierarchy is designed to be "Editorial Industrial"—large, bold headlines that command attention, paired with compact, high-density labels for data.

*   **Display (Display-LG/MD):** Used for key metrics and high-level warehouse health. Bold weight.
*   **Headline (Headline-SM):** 1.5rem. Used for section titles. This should feel "heavy" and permanent.
*   **Title (Title-SM):** 1rem. Used for card headers.
*   **Body (Body-MD):** 0.875rem. The workhorse for all descriptions.
*   **Label (Label-MD/SM):** 0.75rem. Used for metadata and status. These should often be all-caps with slight letter-spacing (+0.05em) to enhance the industrial aesthetic.

---

## 4. Elevation & Depth: Tonal Layering
Traditional "drop shadows" are forbidden unless used for temporary, floating elements. We achieve depth through the **Layering Principle**.

*   **Ambient Shadows:** For floating elements (Modals, Popovers), use an extra-diffused shadow: `box-shadow: 0 12px 40px rgba(23, 28, 31, 0.06);`. The shadow color is a tinted version of `on-surface`, never pure black.
*   **The "Ghost Border" Fallback:** If a container requires definition against a background of the same color, use the `outline-variant` token at **15% opacity**. This creates a "perception of an edge" without the visual clutter of a line.
*   **Corner Radii:** Apply a strict `0.75rem` (md) to cards and `0.5rem` (DEFAULT) to buttons/inputs. This creates a "precise" rather than "bubbly" feel.

---

## 5. Components: Industrial Primitives

### Buttons
*   **Primary:** Solid `primary` background. No border. White text. Subtle gradient from center.
*   **Secondary:** `surface-container-highest` background. Dark gray text.
*   **Tertiary:** Ghost style. No background until hover. Use for low-priority actions like "Cancel."

### Cards & Lists (The Divider-Free Approach)
*   **Standard Card:** Use `surface-container-lowest` (#ffffff) with an `8px` vertical gap. Forbid horizontal lines. Use white space and `label-sm` metadata to separate list items.
*   **Industrial Data List:** Alternate row colors using `surface-container-low` and `surface` instead of using grid lines.

### Input Fields
*   **Structure:** Semi-flat design. Use `surface-container-low` as the background. On focus, transition to `surface-container-lowest` with a `2px` `primary` bottom-border only. This mimics professional blueprints and technical documents.

### Status Chips
*   **Visual Style:** Small, compact, and high-contrast. Use `tertiary-container` for backgrounds with `on-tertiary-container` text. Avoid large, rounded "pills"; use the `0.25rem` (sm) radius for a more "tag-like" industrial feel.

---

## 6. Do’s and Don'ts

### Do:
*   **Do** use 24px or 32px padding for large containers to give data "room to breathe" despite the industrial theme.
*   **Do** use `on-surface-variant` for secondary text to maintain a strict hierarchy.
*   **Do** align all icons to a strict 20px or 24px grid to maintain the "Precision Architect" feel.

### Don't:
*   **Don't** use 1px solid borders to separate the sidebar from the main content; let the color shift do the work.
*   **Don't** use standard "Select" dropdowns. Use custom, tonal-layered menus that match the card depth.
*   **Don't** use pure black (#000) for text. Use `on-surface` (#171c1f) for better readability against the gray-blue background.
*   **Don't** use vibrant, neon colors. Stick to the Material-derived palette to maintain a "High-End Editorial" seriousness.

---
**Director’s Final Note:** *The goal is to make the user feel like they are operating a multi-million dollar machine, not a social media app. Every pixel must feel intentional, structural, and weighted.*