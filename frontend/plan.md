# STUDY BUDDY — PREMIUM FRONTEND UI/UX MASTER PROMPT

> **Purpose:** This document is the creative direction, product experience specification, and implementation brief for designing and building the Study Buddy frontend.
>
> **Audience:** A top-tier product designer, brand designer, design systems engineer, and senior frontend engineer—or an AI agent acting with the combined judgement of that team.
>
> **North star:** Create a distinctive, emotionally engaging, trustworthy learning environment that feels like a carefully art-directed premium education brand. It must feel human, editorial, tactile, confident, and memorable—not like a generic AI dashboard or an AI-generated SaaS template.

---

## 1. THE ROLE YOU MUST PLAY

Act as a multidisciplinary team consisting of:

- A top 1% product and UX designer with strong consumer-brand instincts.
- A premium brand identity and art-direction specialist.
- A senior interaction designer who understands learning behaviour and user motivation.
- A design systems architect.
- A senior responsive frontend engineer who cares about accessibility, performance, maintainability, and detail.

Do not rush into writing components. First understand the existing Study Buddy product, inspect the repository and its backend contracts, identify the real user journeys, and then translate this brief into a coherent experience.

Make deliberate design decisions. Explain important trade-offs briefly in implementation notes. Do not invent backend capabilities, data, metrics, integrations, or trust claims.

## 2. PRODUCT AND BRAND FOUNDATION

### Product
Study Buddy is a document-grounded AI study companion. A learner can bring their own study materials, ask questions about those materials, understand difficult concepts, revise important points, and prepare for exams.

The experience should make a student feel:

- **Confident:** “I understand what I am studying, and I know where my answers come from.”
- **In control:** “My materials, study sessions, and learning flow are organised.”
- **Motivated:** “I want to keep learning and make progress.”
- **Safe:** “My uploaded material and conversations are handled transparently.”
- **Valued:** “This product feels thoughtfully made for me, not mass-produced.”

### Brand personality
Build the brand around five qualities:

1. **Trustworthy** — clear provenance, honest system states, privacy-conscious language, predictable interactions.
2. **Energetic** — a sense of forward motion, curiosity, achievement, and discovery.
3. **Premium** — considered typography, excellent spacing, refined surfaces, precise details, and editorial composition.
4. **Warm and human** — approachable language, subtle personality, no robotic or corporate stiffness.
5. **Intelligent but understated** — sophisticated utility without shouting “AI” in every section.

### Brand promise
**Your materials. Your understanding. Your progress.**

Treat this as a creative direction, not mandatory final marketing copy. Refine it if a stronger line emerges while preserving the promise.

## 3. ART DIRECTION: DISTINCTIVE, NOT GENERIC AI

The visual result must look like a real product created by an experienced human design studio.

### Desired visual qualities
- Editorial composition and strong visual hierarchy.
- Warm, eye-comforting backgrounds with rich, intentional contrast.
- Expressive display typography paired with exceptionally readable body text.
- A recognisable brand colour system rather than arbitrary colourful cards.
- Confident whitespace, rhythm, alignment, and grid discipline.
- Subtle texture or material character only where it improves the experience.
- A balance of calm study surfaces and energetic moments of progress.
- Purposeful asymmetry and varied composition where appropriate.
- Thoughtful empty states, loading states, hover states, and transitions.
- Consistent visual language across landing, dashboard, library, and study workspace.

### Explicitly avoid
- Generic AI/SaaS dashboard templates.
- A page made entirely of identical rounded cards.
- Excessive glassmorphism, blur, neon glow, and glowing borders.
- Purple-blue-pink gradients used as a substitute for brand identity.
- Random decorative blobs, floating orbs, sparkles, and meaningless illustrations.
- Overuse of emojis, robot imagery, circuit patterns, and AI brain graphics.
- Excessively rounded everything, pill-shaped everything, and oversized buttons.
- Tiny low-contrast labels and dense dashboard clutter.
- Repetitive three-column feature cards and predictable template sections.
- Fake charts, fake usage metrics, fake testimonials, fake ratings, or fake trust badges.
- Animations that distract from reading or slow down studying.
- An interface that looks like a prompt-generated mockup rather than a finished product.

Do not use visual effects just because they are fashionable. Every visual decision must have a reason.

## 4. COLOUR AND THEME DIRECTION

Create a cohesive colour system with semantic tokens. The following is a starting art direction, not permission to apply every colour everywhere. Tune the final palette for contrast and visual harmony.

### Core palette direction

| Role | Suggested direction | Purpose |
|---|---|---|
| Primary ink | Deep midnight / blue-charcoal | Authority, clarity, premium contrast |
| Brand primary | Deep teal / refined blue-green | Trust, focus, intelligence |
| Brand accent | Warm amber / golden ochre | Progress, achievement, optimism |
| Secondary accent | Muted coral / terracotta | Human warmth and selected highlights |
| Light canvas | Warm ivory / soft parchment | Comfortable long reading sessions |
| Elevated surface | Clean warm white | Content separation and clarity |
| Dark canvas | Rich charcoal / midnight green | Comfortable dark environment |
| Dark elevated surface | Layered graphite / deep teal-charcoal | Depth without harsh contrast |
| Supporting neutral | Stone / warm grey | Quiet supporting information |

Use restrained accents. The brand should be recognisable even when viewed in grayscale.

### Light mode
- Make warm ivory or a similarly soft neutral the primary canvas.
- Use dark, high-legibility text.
- Use restrained brand colour for primary actions, active navigation, focus, and meaningful emphasis.
- Keep cards and panels distinct through subtle surface changes, borders, and spacing—not heavy shadows.
- Ensure long reading sessions feel comfortable.

### Dark mode
- Design dark mode intentionally; do not simply invert the light theme.
- Use deep charcoal or midnight-toned backgrounds, not pure black everywhere.
- Preserve the brand's teal and warm accent identity while adjusting brightness and saturation for comfort.
- Maintain clear surface layering, text hierarchy, focus states, and code/document readability.
- Verify contrast for muted text, borders, icons, and disabled controls.
- Avoid large areas of saturated colour that cause eye strain.

### Theme behaviour
- Provide a visible theme control in the global interface.
- Support Light, Dark, and System preferences.
- Persist the user's explicit choice where the existing application architecture supports it.
- Prevent a bright flash when loading a saved dark theme.
- Ensure every screen, dialog, menu, tooltip, editor, and loading state supports both themes.
- Never leave hard-coded light-only colours in components.

Define tokens for canvas, surface, elevated surface, text primary/secondary/muted, border, brand primary, brand accent, success, warning, danger, focus ring, overlay, and interactive states.

## 5. TYPOGRAPHY: EXPRESSIVE, CURVY, AND READABLE

Typography is a major part of the brand. It should feel rich, confident, elegant, and slightly expressive without compromising readability.

### Recommended typographic direction
Explore a pairing such as:
- **Display/headings:** Fraunces or another distinctive, characterful editorial serif with elegant curves.
- **Interface/body:** Manrope, DM Sans, or another polished humanist/geometric sans-serif with excellent screen readability.
- **Technical metadata:** A restrained monospace only where genuinely useful.

You may propose a better pairing, but explain why it suits the brand. Check actual font availability and loading strategy. Prefer reliable, performant font delivery and sensible fallbacks.

### Type principles
- Use medium-to-large display typography for major page headings and meaningful moments.
- Give headings personality through weight, line height, letter spacing, and carefully controlled line breaks.
- Use a clear hierarchy: display, page title, section heading, card title, body, supporting text, caption, and metadata.
- Keep body copy comfortably readable; do not shrink text to fit a design.
- Avoid ultra-thin font weights and excessive all-caps labels.
- Use boldness selectively. Do not make every line compete for attention.
- Use fluid responsive sizing with sensible minimums and maximums.
- Maintain readable line lengths for learning content.
- Typography must remain beautiful and legible in both themes.

## 6. INFORMATION ARCHITECTURE AND CORE SCREENS

Design the complete user journey, not just a dashboard screenshot.

### A. Brand landing / welcome experience
If the product requires a public landing page, create a distinctive introduction that communicates:
- What Study Buddy does in plain language.
- How a learner brings their own materials.
- How answers connect to those materials.
- The value of guided learning and revision.
- A clear primary action to begin or enter the workspace.

Use real product UI previews or carefully composed product screenshots if available. Do not use fake customer logos, fake testimonials, or fabricated statistics.

### B. Authentication and onboarding
Design clean, reassuring sign-up, login, and guest entry flows according to actual backend capabilities.
- Keep forms focused and easy to complete.
- Explain errors in helpful language.
- Include password visibility and accessible validation where applicable.
- Clearly communicate what happens after account creation.
- Do not promise guest persistence or account features unless implemented.
- Keep the visual identity consistent with the main product.

### C. Main dashboard / study home
The dashboard should feel like a personal learning studio—not a corporate analytics dashboard.

Prioritise:
- A welcoming, meaningful greeting without excessive decoration.
- A clear “continue studying” or “start a study session” action.
- Recent or active study sessions, if supported.
- A document library entry point.
- A simple upload action with accepted file formats and size guidance based on actual backend limits.
- Useful learning-mode entry points.
- Empty states that guide first-time users toward their first useful action.

Do not invent progress data. If there is no data, design an intentional and motivating empty state.

### D. Document library
Design a useful, calm library for uploaded learning material:
- Document title, file type, upload status, and relevant metadata.
- Search, filtering, and sorting only when supported.
- Clear processing, success, and failure states.
- Actions that are obvious and safe.
- Helpful empty and error states.
- Responsive list/grid presentation that does not waste screen space.

### E. Study session workspace — the signature experience
This is the most important screen. It should be the strongest expression of the brand.

The workspace should feel like a premium, focused learning environment: immersive but not distracting, rich but not cluttered.

Include, where supported:
- A dedicated study-session header/navigation bar.
- Current document or selected material context.
- Session title and a clear way to return to the library/dashboard.
- A focused conversation/learning area.
- A well-designed message composer.
- Clear answer loading and streaming states.
- Source/document context so users understand what material informs an answer.
- Useful conversation history or session navigation if persistence exists.
- Learning mode controls.
- A calm, visible indication of whether the assistant is answering from uploaded material, when the backend can verify this.
- Helpful recovery actions when no relevant material is found.

#### Study-session navigation bar: trust and clarity
Design a distinctive session navbar that communicates confidence and orientation.

It should make clear:
- Where the learner is.
- Which document or study context is active.
- Whether the material is ready, processing, or unavailable.
- What study mode is active.
- How to access session options or exit safely.

A trust indicator is important, but it must be honest and evidence-based. Prefer precise language such as:
- “Using your selected document”
- “Sources available”
- “No matching source found”
- “Document processing”
- “Answer based on retrieved material”

Only show a status when the backend provides enough information to support it. Do not display a fabricated “100% trusted”, “verified AI”, security score, confidence percentage, or guarantee. If answer citations or source references are not currently implemented, design a clear future-ready slot but do not pretend they work.

The navbar should feel polished and special, with clear active states and a strong visual hierarchy. It must not become a dense toolbar.

### F. Learning modes
Design a consistent mode-selection experience for the modes that the product intends to support:
- **Teach me:** explain a concept in a clear, structured, approachable way.
- **Key points:** extract concise, useful revision points.
- **Quiz me:** help the learner test understanding.
- **Exam tips:** surface relevant preparation guidance.

Modes should be recognisable and easy to switch. Use restrained icons, strong labels, and meaningful active states. Do not rely on colour alone. The selected mode should be visible in the session context.

Do not imply a mode is functional until its backend behaviour exists. Distinguish implemented functionality from planned UI.

### G. Conversation and answer design
Learning content deserves excellent typography and layout.
- Make assistant answers easy to scan without turning every sentence into a card.
- Support headings, paragraphs, numbered steps, bullets, code, tables, and citations as applicable.
- Distinguish user and assistant messages with subtle but clear visual language.
- Make source references legible and useful.
- Provide copy or other message actions only when functional.
- Keep the composer comfortable to use on desktop and mobile.
- Preserve message readability and context while streaming.
- Handle long answers, empty responses, network errors, and retry states gracefully.

## 7. NAVIGATION AND RESPONSIVE STRUCTURE

Create a navigation system that is simple, memorable, and consistent.

### Desktop
- Use a considered global navigation for the main product areas.
- Use a dedicated study-session navigation/header when inside a session.
- Keep primary actions visually clear.
- Avoid overloading the top bar with every possible control.
- Use a sidebar only if it materially improves navigation and remains visually light.

### Tablet
- Reflow layouts intelligently.
- Keep essential navigation and actions reachable.
- Do not merely shrink desktop components.
- Allow panels to collapse or move into accessible drawers where appropriate.

### Mobile
- Design mobile as a first-class experience, not a compressed desktop.
- Use a compact, purposeful header and appropriate mobile navigation.
- Make the composer and primary actions thumb-friendly.
- Ensure dialogs, menus, upload flows, and document previews fit small screens.
- Avoid horizontal overflow.
- Keep reading widths and line heights comfortable.
- Ensure the keyboard does not obscure the active composer or essential controls.
- Use bottom navigation only if it improves the actual information architecture; do not add it by default.

### Responsive breakpoints
Choose and document breakpoints based on content needs, not device marketing labels. Test narrow phones, large phones, tablets, laptops, and wide desktop screens.

## 8. INTERACTION DESIGN AND MICRO-DETAILS

Every interactive element must have a complete state model.

Specify and implement:
- Default, hover, active, focus-visible, disabled, loading, success, and error states.
- Clear button hierarchy: primary, secondary, tertiary, destructive, and icon-only.
- Accessible menus, popovers, dialogs, and drawers.
- Useful upload progress and file-processing feedback.
- Empty, skeleton/loading, retry, and offline/network-error states.
- Form validation and helpful inline feedback.
- Toasts or notifications only when they communicate meaningful events.
- Clear confirmation for destructive actions.
- Predictable navigation and back behaviour.

### Motion and transitions
Use motion to make the product feel responsive and alive, not theatrical.
- Prefer subtle transitions, gentle easing, and short durations.
- Use motion to communicate state changes, focus, progress, and hierarchy.
- Avoid constant movement, bouncing, parallax overload, and decorative animation loops.
- Respect reduced-motion preferences.
- Ensure animation never delays a critical action or makes content harder to read.

## 9. ACCESSIBILITY, COMFORT, AND TRUST

Treat accessibility as part of premium quality.

- Aim for WCAG 2.2 AA contrast and interaction standards.
- Use semantic HTML and a logical heading structure.
- Support keyboard navigation throughout.
- Provide visible focus indicators.
- Give icon-only controls accessible names.
- Associate form fields with labels and clear error messages.
- Do not rely on colour alone to convey state.
- Respect reduced-motion settings.
- Ensure touch targets are comfortably sized.
- Test zoom and text resizing.
- Ensure light and dark themes both meet contrast requirements.
- Use plain, honest language around data, documents, and AI-generated responses.

The interface must not claim that documents are private, encrypted, deleted, or never used for training unless those claims are confirmed by the actual product architecture and policies. Trust is earned through clarity, not badges.

## 10. DESIGN SYSTEM AND COMPONENT QUALITY

Build a coherent, reusable system rather than styling each page independently.

Define:
- Colour and semantic theme tokens.
- Typography scale and font roles.
- Spacing scale and layout grid.
- Border, radius, elevation, and shadow rules.
- Icon style and sizing.
- Button variants and sizes.
- Form controls.
- Navigation patterns.
- Cards and panels where appropriate.
- Dialogs, dropdowns, tooltips, tabs, and toast patterns.
- Message and source-reference patterns.
- Loading, empty, success, warning, and error patterns.

Use a consistent icon family and stroke weight. Avoid mixing unrelated icon styles or using emoji as the primary icon system.

Components should be composable, accessible, responsive, and easy to maintain. Avoid one-off CSS hacks and duplicated styles.

## 11. TECHNICAL IMPLEMENTATION RULES

Before implementation:

1. Inspect the existing frontend directory and repository structure.
2. Inspect the backend API routes, schemas, authentication flow, upload flow, chat flow, and response formats.
3. Identify the actual frontend framework and tooling already selected. Do not assume React, Next.js, Vite, or any other stack without checking.
4. Identify the API base URL and existing environment-variable conventions without exposing secret values.
5. Map each proposed screen and interaction to a real API capability.
6. List missing backend capabilities separately; do not fake them in the frontend.
7. Preserve existing work and avoid unrelated backend changes.

During implementation:
- Use the existing project stack unless a change is justified and approved.
- Keep components modular and name them clearly.
- Separate API access, application state, reusable UI, and page composition.
- Handle loading, empty, success, and error states for every network-dependent flow.
- Keep credentials and API secrets out of frontend source code.
- Never expose the Groq API key, database credentials, JWT signing secret, or other backend secrets in browser code.
- Use environment variables only for values that are safe to expose to the client.
- Do not put secrets in local storage.
- Avoid unnecessary dependencies.
- Avoid mock data in production paths. If mock data is needed for a design preview, isolate it and label it clearly.
- Keep performance in mind: lazy-load heavy views and avoid shipping unnecessary assets.
- Do not weaken authentication or backend validation to make the UI appear functional.

## 12. CONTENT AND BRAND VOICE

The product voice should be:
- Clear, encouraging, intelligent, and respectful.
- Confident without being boastful.
- Warm without being childish.
- Motivating without guilt or pressure.
- Concise in controls and helpful in explanations.

Prefer specific language over generic AI phrases.

Avoid repetitive copy such as:
- “Unlock the power of AI”
- “Revolutionise your learning”
- “Your AI-powered journey starts here”
- “Supercharge productivity”

Use language that describes real learner outcomes and real product behaviour.

## 13. QUALITY BAR AND ACCEPTANCE CRITERIA

The work is not complete merely because the pages render.

### Brand and visual quality
- The product has a distinctive visual identity.
- It looks art-directed and intentional, not template-generated.
- Typography, colour, spacing, and composition work as one system.
- The experience feels premium without being visually exhausting.
- The session workspace is the strongest and most polished screen.

### UX quality
- A first-time user can understand how to begin.
- A returning user can locate materials and continue a session.
- Upload and processing states are understandable.
- The active study context is always clear.
- Trust indicators reflect real backend evidence.
- Important actions are easy to find.
- Empty, error, and success states are fully designed.

### Responsive quality
- No horizontal overflow at tested widths.
- No clipped menus, dialogs, or content.
- Mobile composer remains usable with the keyboard open.
- Navigation adapts appropriately across screen sizes.
- Typography and spacing remain intentional on all devices.

### Accessibility quality
- Keyboard navigation works.
- Focus is visible.
- Controls have accessible names and labels.
- Colour contrast is checked in both themes.
- Reduced motion is respected.
- Status is not conveyed by colour alone.

### Engineering quality
- The application starts using the documented project command.
- No avoidable console errors or failed asset requests.
- API errors are handled gracefully.
- No secrets are exposed to the client.
- No fake product capabilities are presented as working features.
- Components and styles are maintainable.
- Existing backend contracts are respected.

## 14. REQUIRED WORKFLOW AND DELIVERABLES

Work in this sequence. Do not skip directly to a pile of components.

### Phase 1 — Discovery
- Inspect the full frontend and relevant backend.
- Identify current stack, entry points, API routes, schemas, and existing assets.
- Record what exists, what is incomplete, and what is unknown.
- Do not change backend code as part of frontend design unless explicitly authorised.

### Phase 2 — Experience blueprint
Produce:
- User journeys for first-time and returning learners.
- Information architecture and navigation map.
- Screen inventory and each screen's purpose.
- Core task flows for authentication, upload, library, study session, and learning modes.
- Mapping of UI actions to actual backend endpoints.
- A list of unavailable or future capabilities.

### Phase 3 — Brand and design system
Produce:
- Brand direction and visual rationale.
- Final colour palette with semantic tokens and hex values.
- Light and dark theme tokens.
- Typography pairing, scale, weights, and responsive rules.
- Spacing, grid, radius, border, elevation, and icon rules.
- Component inventory and interaction states.

### Phase 4 — High-fidelity screen design
Design the key screens as a consistent family:
1. Welcome / entry.
2. Sign up and login.
3. Main dashboard.
4. Document upload and processing.
5. Document library.
6. Study session workspace.
7. Learning mode selection and states.
8. Profile/settings and theme preferences, if supported.

Prioritise the study-session workspace and demonstrate its trust/navigation design clearly.

### Phase 5 — Frontend implementation
- Implement the design system first.
- Build reusable components.
- Implement responsive screens.
- Connect real backend functionality where available.
- Add robust loading, empty, error, and success states.
- Keep future features clearly separated from working functionality.

### Phase 6 — Verification and refinement
- Run the app and test the complete user journeys.
- Test light and dark themes.
- Test desktop, tablet, and mobile.
- Check keyboard navigation and accessibility.
- Inspect console and network errors.
- Refine visual rhythm, spacing, typography, and micro-interactions.
- Compare the final implementation against every acceptance criterion.

### Final handoff
Provide:
- A concise summary of the visual direction.
- A screen and component inventory.
- The final token/palette and typography decisions.
- What is implemented and connected to the backend.
- What remains blocked by missing backend functionality.
- How to run the frontend.
- Any known limitations and recommended next steps.

## 15. FINAL CREATIVE INSTRUCTION

Create a learning product people genuinely enjoy returning to.

The emotional experience should move between:
- **Calm focus** while reading and understanding.
- **Curiosity and excitement** when exploring a concept.
- **Confidence** when an answer is grounded in their material.
- **Satisfaction** when completing a learning task.
- **Loyalty** through a consistent, recognisable, thoughtful product experience.

Make the product feel like a premium personal learning studio: expressive typography, warm and confident colour, excellent content design, considered navigation, subtle energy, and exceptional usability.

Do not confuse luxury with decoration. Luxury is precision, restraint, consistency, responsiveness, and care.

Do not confuse excitement with visual noise. Excitement is purposeful contrast, strong hierarchy, moments of delight, and a sense of progress.

Do not confuse trust with a badge. Trust is transparency, accurate states, reliable interactions, and honest product behaviour.

**The final result must look and feel like a distinctive, professionally art-directed education brand—not an AI template.**
