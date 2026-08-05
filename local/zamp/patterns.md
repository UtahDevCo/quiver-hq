# Coding Patterns

Recurring patterns derived from PR review feedback and team conventions.

> Source artifact. This is the raw distillation Chris supplied on 2026-08-05.
> Operational review checks from here are merged into
> `agents/pr-review.local.md` ("Zamp convention checklist"); the cross-project
> practices are proposed into `brain/inbox/` as OKF Observations. Keep this file
> as the citable original — downstream concepts reference it in `sources:`.

---

## Design System & UI Components

### Storybook is the source of truth for design-system components

Before reaching for a `@util/design-system` component, check its Storybook (`*.stories.tsx`) for canonical usage. Don't grep for call sites and copy — older call sites can predate conventions or have them backward (e.g. `nps-survey.client.tsx:114` nests `<FieldGroup><FieldSet>` while the canonical order is `<FieldSet><FieldGroup>`, demonstrated in the Field/FieldSet stories). Storybook entries are curated to demonstrate intent; call sites are not.

### Use `@util/design-system`, never legacy packages

`@util/ui` is deprecated. All new code uses `@util/design-system`.

### Use `Button`, not `RtButton`

`RtButton` is legacy. Mapping: `color="gray" variant="soft"` → `variant="secondary"`, `variant="solid"` → default.

### Button handles its own text styling

Don't wrap Button children in `<Text>`. The Button component styles text internally.

### Button `loading` prop disables automatically

Don't add redundant `disabled={isPending}` when `loading` is set.

### Buttons that navigate are links

If a button's `onClick` just changes the route, use a `<Link>` (or `<Button asChild><Link>`). Navigation is a link, not a button action.

### Use `Strong` over `Text weight="bold"`

`<Strong>` is semantically correct for bold inline text.

### Use `Label` for form field labels

Use `<Label>` from design-system, not `<Text weight="medium">`.

### Use `EmptyDash` for empty values

There's an `EmptyDash` component in the DS for displaying absent values.

### Don't specify default prop values

E.g., `<Icon size={16}>` — 16 is the default, omit it.

### Only use `Text` when modifying text

Don't wrap plain text in `<Text>` unless you're changing size, weight, or color.

### Use `Select` over `DropdownMenu` for value selection

`DropdownMenu` is for actions (paired with icon buttons). `Select` is for choosing a value.

### Disable options vs empty states

If an option requires missing data, disable the option. Don't show a confusing empty state when selected.

### Use `<Icon icon="..." />` from design-system

Use the design-system `Icon` component for all icons **in application code and DS wrappers' own composition**. This does **not** apply inside `utils/design-system/src/components/shadcn/*` — those files are treated as third-party, keep their lucide imports as-is, and DS wrappers that re-export shadcn sub-components don't override the lucide icons inside them. See `select`, `dialog`, `sheet`, `dropdown-menu`, `pagination` — all re-export shadcn sub-components verbatim, lucide icons and all. Don't "fix" this by swapping in DS `Icon` at the wrapper level; you'll diverge from four established precedents to chase a rule that's aimed at app code.

### Use Tailwind for layout, not the deprecated Radix Themes wrappers

`Flex`, `Box`, `Grid`, `Container`, and `Section` from `@util/design-system` are `@deprecated` (see `utils/design-system/src/components/radix-components.ts`). They wrap Radix Themes and don't compose with the rest of the DS. Reach for Tailwind utilities on a plain element instead.

```tsx
// ❌ Deprecated Radix Themes wrappers
<Flex justify="between" align="start" gap="3">…</Flex>
<Box px="4" py="2">…</Box>

// ✅ Tailwind on a plain element
<div className="flex items-start justify-between gap-3">…</div>
<div className="px-4 py-2">…</div>
```

### Let parents handle positioning

Don't add positioning wrappers on child components. The parent layout should handle positioning.

### All new DS components need Storybook stories

Canonical reference: `badge.stories.tsx`. The shape:

- **`Default` story** is the playground: `StoryObj<DefaultStoryProps>` with `argTypes` (select / text controls per prop), `args` (the defaults), and `parameters: { docs: { description: { story: "..." } } }` for the description.
- **Showcase stories** (`Variants`, `Colors`, `Sizes`, etc.) are pure render functions. No `argTypes`, no `parameters` block. Add a JSDoc above the `export` only when it conveys something the rendered output doesn't (a caveat, non-obvious guidance) — restating "this story shows the variants" is restating the story name.
- **Section labels** inside showcase renders: `<span className="font-text-xs font-bold">`, not `<p className="text-sm">`.
- **Iterate a module-level `as const` array** (e.g. `const colors = [...] as const;`) when enumerating multiple variants across stories.
- **Don't add `modes: true`** — convention shifted away from per-story modes.

### Read defaults before overriding

Before adding a class, prop, attribute, or `aria-*` to a primitive, read what it (and its underlying HTML element) already provides. Defaults come from several places:

- **DS primitives** — `Card` sets `text-card-foreground`; `Item size="default"` sets `gap-3.5 px-4 py-3.5`; `Sheet[side=right]` caps `sm:max-w-sm`; `Icon` defaults to `size={16}`.
- **Parent layout** — if the wrapper is `flex flex-col gap-4`, your children don't need their own `flex flex-col gap-4` wrapper. If `FailureDetailSheet`'s body already provides `flex flex-1 flex-col gap-4`, the table component returns a Fragment, not a div re-declaring the same layout.
- **HTML elements** — anchors get pointer cursors; `<button>` is keyboard-focusable and clickable without `"use client"`; a button's visible text *is* its accessible name (don't override with a conflicting `aria-label`).
- **React/JSX** — boolean props default to `true`, so `open={true}` is `open`.

Re-applying a default the primitive already gives you is dead weight. It hides the real custom overrides in noise, and it silently drifts when the primitive evolves.

### Flex column children stretch by default

In a flex column, every child has `align-items: stretch` unless you say otherwise. Three consequences:

- **`w-full` on a flex-column child is almost always redundant.** Drop it.
- **To opt one child out of stretch, use `self-start` (or `self-end`/`self-center`) on _that child_** — don't add `items-start` to the parent (it un-stretches every sibling), and don't wrap the child in a div just to break the stretch chain.
- **Parent `items-center` is redundant when every child centers its own contents.** A child with `text-center`, an internal `flex flex-col items-center`, or a full-width DS container (e.g. `ItemGroup`) already handles its own alignment. Adding `items-center` to the parent duplicates that and prevents children from stretching to full width when they'd otherwise want to. Reach for parent `items-*` only when children have intrinsic widths that need shared alignment.

```tsx
// ❌ Wrapper div purely to prevent the Button from stretching
<ContentWrapper>
  <div><Button size="sm" /></div>
  <Separator />
  {children}
</ContentWrapper>

// ✅ Opt the one child out, let Separator and children stretch
<ContentWrapper>
  <Button size="sm" className="self-start" />
  <Separator />
  {children}
</ContentWrapper>

// ❌ Parent items-center duplicates each child's internal centering
<Item className="flex-col items-center gap-10">
  <div className="text-center">…</div>
  <ItemGroup>…</ItemGroup>
  <div className="flex flex-col items-center gap-4">…</div>
</Item>

// ✅ Let children stretch; each already centers its own contents
<Item className="flex-col gap-10">
  <div className="text-center">…</div>
  <ItemGroup>…</ItemGroup>
  <div className="flex flex-col items-center gap-4">…</div>
</Item>
```

### Reach for DS container primitives over wrapper divs

When stacking the same DS primitive (rows of `Item`, cards of `Card`, etc.), look for a matching DS container before writing `<div className="flex flex-col gap-N">`. `ItemGroup` wraps `Item`s. `CardGrid` (where it exists) wraps `Card`s. Containers carry the canonical spacing and any role/`aria` plumbing — a hand-rolled flex wrapper has none of that.

### Use the `PageHeader` family for page top, not `Container` + raw `<h1>`

New pages compose `ContentWrapper` + `PageHeader` + `PageHeaderTitle` + `PageHeaderActions` from `@util/design-system`. The family handles responsive grid (`md:grid-cols-[2fr_2fr]`), page padding (`px-4 md:px-6 lg:px-16`), and title typography in one place. Duplicating that with `Container` + flex `<div>` + `<h1 className="font-page-title">` is what `PageHeader` exists to absorb. `Container` is fine for non-page-level layouts, but the moment you reach for `<h1 className="font-page-title">` or a header-row flex wrapper, switch to the family.

```tsx
// ❌ Hand-rolled page top
<Container align="left">
  <div className="flex items-start justify-between gap-3">
    <h1 className="font-page-title">{title}</h1>
    <SomeAction />
  </div>
  {children}
</Container>

// ✅ Composed from the DS family
<ContentWrapper>
  <PageHeader>
    <PageHeaderTitle>{title}</PageHeaderTitle>
    <PageHeaderActions>
      <SomeAction />
    </PageHeaderActions>
  </PageHeader>
  {children}
</ContentWrapper>
```

### Check for re-exported shadcn slot primitives before writing styled HTML

`@util/design-system` re-exports many shadcn slot primitives unchanged — they pass straight through from `./shadcn/*`, no wrapper. They're easy to miss because they don't show up as `function Foo()` in the DS source; they sit in `export { Foo } from "./shadcn/..."` lines. Examples shipped today:

- `SheetDescription`, `SheetHeader`, `SheetFooter`, `SheetTitle` (from `sheet.tsx`)
- `AlertTitle`, `AlertDescription`, `AlertAction` (from `alert.tsx`)
- `CardTitle`, `CardDescription` (from `card.tsx`)
- `ItemTitle`, `ItemDescription`, `ItemHeader`, `ItemFooter`, `ItemSeparator`, `ItemGroup`, `ItemActions`, `ItemContent`, `ItemMedia` (from `item.tsx`)
- `EmptyTitle`, `EmptyDescription`, `EmptyHeader`, `EmptyMedia`, `EmptyContent` (from `empty.tsx`)

Before rendering `<p className="text-muted-foreground">` for a description, or a styled `<div>` for a header/footer slot, grep the relevant DS source for slot exports. Slot primitives carry not just the typography but the underlying Radix wiring — `SheetDescription` (which is Radix `Dialog.Description`) sets `aria-describedby` on the dialog automatically; a hand-rolled `<p>` doesn't.

**Verify the primitive's defaults fit before adopting it.** Three ways the primitive may be wrong:

- **Wrong semantic element.** `EmptyTitle` and `CardTitle` render as `<div>`, not `<h1>`/`<h2>`. If accessible heading rank matters, a plain semantic tag with a font utility (`<h1 className="font-page-title">`) beats the styled-div primitive.
- **Bundled rules you don't want.** `ItemDescription` is a `<p className="text-muted-foreground text-sm">` — but it also adds `line-clamp-2` and `[&>a]:underline`. If your description has line breaks you want preserved or no links, the plain `<p>` is cleaner than overriding the primitive's extras.
- **Wrong semantic role for your content.** A slot named `Description` doesn't mean "any paragraph that describes things." `SheetDescription` is sized for a short one-line subtitle (`text-sm text-muted-foreground`) and is labelling copy for the dialog. Putting a 3-line explanatory paragraph in it makes the header wall-of-text and competes visually with the title. Body-shaped prose belongs in the body, not in a header slot whose role is labelling. Test: would a screen reader announcing this with the dialog's accessible name make sense as a subtitle, or does it read like a sentence the user is meant to actually consume?

### Figma's element tree is a reference, not a literal target

The designer's job is to communicate the visual outcome. Their layer panel ("Card → Frame → Auto Layout → Frame…") describes _their_ tool, not your component tree. If a DS `Item` with `variant="outline"` and the right padding produces the same look as their "Card," use the `Item`. Replicating every Figma frame as a `<div>` is how you end up with five levels of nesting that all do the same thing one DS variant does.

### Size content via container padding, not child widths

To make rows look ~448px wide inside a 672px card, set horizontal padding on the card (`w-2xl px-28`), and let the children fill naturally. Don't set `w-md` on each row. Padding-on-container scales with one number; widths-on-children must agree across every child and break the moment the design changes.

### Inline UI copy in JSX rather than centralized copy tables

The dominant pattern (`apps/company/(onboarding)/...` throughout) is each component hardcoding its own JSX strings. Designers and PMs can grep the rendered text and land directly on the component. `Record<Key, string>` lookup maps for customer-facing prose split copy from its render context.

```typescript
// ✅ Inline — copy lives next to its render site
<Heading>We need a few more details</Heading>

// ❌ Centralized lookup — copy hidden behind a key
<Heading>{COPY.title}</Heading>
```

Centralized maps are only right when a single aggregator needs every entry — e.g. `get-onboarding-ui-state.ts` building a typed list for a nav.

### Wrap form Fields in FieldSet + FieldGroup

Don't render `<Field>` directly inside `<form>`. Use `<FieldSet><FieldGroup><Field>…</Field></FieldGroup></FieldSet>` (note nesting order: `FieldSet` is outer). `FieldGroup` handles consistent field-to-field spacing; doing it manually with form-level Tailwind drifts from the design system. The submit button can live inside `FieldGroup` to pick up the same spacing for free. Reference: `team-member-dialog.client.tsx:180-219`.

### Split polymorphic components when the discriminator is structural

When a single component's prop union discriminates on "do we have data X yet?" (e.g. pending vs resolved, loading vs loaded), prefer two sibling components with flat prop types over one polymorphic component with a discriminated union. The runtime decision moves to JSX-level component choice (`<PendingFoo />` vs `<ResolvedFoo />`), removing the "which variant am I in?" branching from every render path inside the component. Each component's prop type stays 2-5 flat fields. Internal sub-discriminators (e.g. pass vs fail within Resolved) can stay inside the component as plain runtime branching on a value like `count === 0`. Reference: `PendingImportCheckRow` / `ResolvedImportCheckRow` in the AI CSV import flow.

### Authoring shared components in `@util/ui-templates`

`@util/ui-templates` is the cross-app home for presentational components reused by multiple apps (company + admin both consume `economic-nexus`, `summary-report`, and the AI-CSV-import `csv-import` module). Its conventions differ from app code:

- **Drop the `.client` suffix.** Client components keep `"use client"` but are named `foo.tsx`, not `foo.client.tsx`. The `.coderabbit.yaml` `.client.tsx` rule is scoped to `apps/**/*.tsx`; the dominant precedent here is suffix-free client files (`auth/impersonate.tsx`, most `summary-report/regions/*.tsx`).
- **Barrels use `export * from "./leaf"`** (precedent: `economic-nexus/index.ts`), not explicit named re-exports — less churn as leaf exports change. This is the *opposite* of `domains/` packages, which forbid barrels.
- **`type` over `interface`** for prop/object shapes (standing repo preference).
- **Compose, don't wrap.** Expose composable pieces and let the consumer arrange them (e.g. `FailureDetailTableHeader` + `FailureDetailTable`, reusing the generic `PaginationControls`) rather than one monolithic wrapper — keeps container concerns like `className` reachable.
- **No test harness** (no `vitest`/`test` script) — don't add unit tests here unless one is set up.
- **Type against `@domain/*`, but a _value_ import can pull server-only deps into the client bundle.** `@domain/import/queries/compute-totals` transitively value-imports `@aws-sdk/client-s3` (via `loadValidatedTransactions`); re-declare small sentinels (`UNCATEGORIZED_TAX_CATEGORY = "UNCATEGORIZED"`) locally instead. Type-only imports are erased and safe.

---

## DataTable Patterns

### Use `DataTable` for paged data, `Table` for static

`DataTable` supports pagination, sorting, filtering. `Table` is for simple static displays.

### Column alignment via `DataTableColumnHeader` and `DataTableCell`

Use `align="right"` (or `"center"`) on header and cell components. Don't hack `meta.width` or add custom meta properties — alignment infrastructure already exists in `headers.tsx` and `cells.tsx`.

### Use `accessorFn` for derived column values

Instead of computing display values inside `cell`, use tanstack's `accessorFn` to prepopulate the data. This enables proper sorting/filtering on the derived value.

### Define `columnHelper` / column config at module level

Don't recreate column definitions inside the component body — it defeats memoization. If columns depend on props, wrap in `useMemo`.

---

## Error Handling

### Don't re-wrap errors

If a helper returns `Err(error)`, return it directly. Don't `Err(new Error("...", { cause: error }))` unless you're adding meaningful context.

### Return result directly on error checks

When checking error results, return the result itself, not a new error wrapping it.

### Server component error handling

Match the pattern to the failure mode:

- **Critical page data not found**: `.isErr()` + `notFound()` — e.g., `companies/[id]/layout.tsx`
- **Suspense-wrapped tables**: `.isErr()` + `captureException` + return error UI row — e.g., `onboarding-specialists-table.tsx`
- **Must-succeed queries**: `.unwrap()` — when failure means the page is fundamentally broken
- **Graceful degradation**: `.unwrapOr(fallback)` or `.isOk() ? result.value : fallback` — for supplementary data (e.g. Clerk member lists). Don't crash the whole page for a secondary fetch failure.

For when to `captureException` vs. throw with `cause` vs. swallow, see the **Error Handling** section in `AGENTS.md` — that's the canonical source.

### `NonRetriableError` is for Inngest only

Don't use `NonRetriableError` outside of background functions. Use regular `Error` in queries and mutations.

### Server action error handling

Use `result.expect(ActionErrorCode.INTERNAL_SERVER_ERROR)` for simple cases. Use `NextSafeActionError` only when you need different error codes (NOT_FOUND vs INTERNAL_SERVER_ERROR).

### User-facing error messages are for users, not engineers

Toast and inline error copy should be actionable plain English, not internal terminology.

```typescript
// ❌ Engineer-speak
toast.error({ description: "Failed to get download URL" });

// ✅ User-actionable
toast.error({ description: "There was a problem downloading the CSV, refresh and try again." });
```

### One throwable per try/catch in mutations with mixed side effects

When a mutation has multiple kinds of side effects (DB + Inngest, DB + S3, etc.), split into helpers. Each helper wraps its own throwable in its own try/catch and returns `Result<T, Error>`. The main mutation orchestrates with `.isErr() → return`.

```typescript
// ✅ Helpers per concern
async function transitionState(...): Promise<Result<void, Error>> {
  try {
    /* DB ops */
  } catch (error) {
    return Err(new Error("Failed to transition", { cause: error }));
  }
}
async function sendEvents(...): Promise<Result<void, Error>> {
  try {
    await inngest.send([...]);
    return Ok(undefined);
  } catch (error) {
    return Err(new Error("Failed to send events", { cause: error }));
  }
}
```

Distinguishable Sentry attribution; tightly-scoped catches don't mask which side effect failed. Older mixed-concern try/catches (e.g. `bulk-toggle-filing-hold.ts`) predate this convention — don't copy them.

---

## Database & Sharding

### Always include `companyId` in WHERE clauses on sharded tables

`Connection`, `SyncHistory`, `Transaction`, and related tables are sharded. Missing `companyId` causes scatter queries (slow, not broken).

### Nested `include` on sharded relations must scope by `companyId`

```typescript
// ✅ Correct
include: { lineItems: { where: { companyId } } }

// ❌ Scatters across all shards
include: { lineItems: true }
```

### Use `ConnectionCompany` lookup table

`utils/db/src/get-connection-company-id.ts` resolves `connectionId → companyId` without hitting the sharded `Connection` table.

### Use transactions for related DB operations

When a read affects whether a create/update happens, wrap in a transaction block.

### Add limits to unbounded queries

`findMany` without a limit will grow unbounded. Always add `take` for lists that can grow.

### Treat migration friction as a first-class cost; prefer metadata-only schema changes

Schema changes in this repo (PlanetScale/Vitess) are a recurring source of friction. Weigh migration cost when choosing a design, and prefer changes that are metadata-only or online-safe over ones that force a table rewrite.

- **Enum values: append, don't mid-insert.** Adding a value at the END of an enum is a metadata-only `ALTER` — no existing value's stored ordinal changes. Inserting one mid-list shifts the ordinals of every later value and forces a full table rebuild. Append the new value even if it breaks the enum's semantic grouping, with a one-line comment so it isn't "tidied" back into the group:

```prisma
enum ImportSessionFailureReason {
  // ...existing values, in their existing order...
  AMOUNT_SANITY // Kept last (out of its group) so the migration is a metadata-only append, not a row-rewriting reorder.
}
```

Keep the generated migration's `MODIFY ... ENUM(...)` list in the same order (existing values unchanged, new value appended).

- Prefer additive forms generally (new nullable column, new table, appended enum value) over rewriting/locking ones (column reorder, type change, `NOT NULL` without a default). For unavoidable rewrites, use expand-migrate-contract.
- Sometimes the lowest-friction migration is none: check whether an existing column/shape, or a non-persisted guard, achieves the goal before adding a column or enum.

---

## React Patterns

### No `forwardRef` in React 19

`ref` as a prop is first-class in React 19. Don't use `forwardRef` for new components.

### Use `PropsWithChildren` for components that take `children`

When a component's props include `children`, type the props as `PropsWithChildren` (or `PropsWithChildren<{...other props}>`) from `react`, not as `{ children: ReactNode }`. It's the dominant codebase pattern across both DS-authoring contributors — Bressain's `apps/company/src/app/(onboarding)/[id]/onboarding/page-components.tsx` and James Walsh's `apps/admin/src/app/components/filing-management/filing-details-sheet.client.tsx` and `apps/admin/src/app/components/activity/activity-feed.tsx` all use it. Reserve the bare `children: ReactNode` shape for cases where you're intentionally typing children narrower than `ReactNode` (e.g. `children: ReactElement<...>`).

```tsx
// ✅ Preferred
import type { PropsWithChildren } from "react";
export function Foo({ children }: PropsWithChildren) { ... }
export function Bar({ children, label }: PropsWithChildren<{ label: string }>) { ... }

// ❌ Avoid for the bare children case
export function Foo({ children }: { children: ReactNode }) { ... }
```

### Define static config outside component body

Column definitions, configuration objects, constants — anything that doesn't depend on props/state belongs at module level. This avoids unnecessary re-renders and makes memoization effective.

### Memoize derived state from props

When computing values from props, wrap in `useMemo` to avoid recomputing on every render.

### Extract multi-effect state machines into a custom hook with a phase enum

When a component has 3+ `useEffect`s driving interrelated state (timers, subscriptions, transitions), extract them into a `use*` hook co-located with the consumer. Expose a single `phase` enum (e.g. `"revealing" | "resolving" | "complete"`) derived internally from counters/data. The phase doubles as the dedupe signal — state transitions are one-way, so guards become `if (phase !== "revealing") return` instead of separate `useRef<boolean>` flags. Reference: `apps/company/src/app/(protected)/[id]/integrations/[connectionId]/import/[sessionId]/use-import-check-animation.ts` (three timer effects + a realtime subscription + a `router.refresh()` behind a four-prop return).

### Server actions are for mutations only

Never use server actions for GET/read operations. Read data directly in async server components.

### Reading data: server components → props → client components

Call domain queries directly in async server components, pass resolved data to client components via props.

### Same-file `*Content` helper for body-of-shell components

When a Page or top-level component owns shell concerns (data fetch, layout, provider context, route params) and the body needs branching or local state, extract a `*Content` helper defined immediately below the export in the same file with its own props type. Dominant onboarding pattern — `ShopifyAppStepContent`, `AccountingFormContent`, `RegionFormContent`, `BankingDetailsFormContent`, `ResponsiblePartyContactFormContent`, etc. — and the shape that the import-session `ImportSessionContent` follows. Cleaner than extracting to a co-located component file when the helper is only consumed by the one wrapper.

### Writing data: `useFormServerAction` / `useAction`

Form submissions go through server actions. `tRPC` and `react-query` for client-side reads/writes are deprecated.

### Don't render hidden inputs for form context

When the form needs non-user-input values (route params, IDs from props), set them via `useForm({ defaultValues })`. react-hook-form's default `shouldUnregister: false` flows defaults into `handleSubmit` without requiring registered DOM inputs.

```tsx
// ❌ Cargo-culted hidden inputs
<input type="hidden" {...form.register("sessionId")} />

// ✅ Defaults thread through to submission automatically
useForm({ defaultValues: { sessionId, note: "" } })
```

If the IDs don't belong in the form schema semantically, skip `useFormServerAction`'s `handleSubmitWithAction` and wrap your own:

```tsx
const onSubmit = form.handleSubmit((data) =>
  action.executeAsync({ ...data, sessionId, connectionId }),
);
```

This separates "what the user enters" (form schema) from "what the action needs" (input schema).

### Prefer `useAction` callbacks over `executeAsync`

Use `onSuccess` / `onError` / `onSettled` for side effects like toasts and navigation. Reach for `executeAsync` only when you genuinely need to await the result inline (e.g., chained async work that can't live in a callback).

```typescript
// ✅ Callbacks handle side effects
const { execute } = useAction(saveFoo, {
  onSuccess: () => toast.success({ description: "Saved" }),
  onError: () => toast.error({ description: "Couldn't save, try again." }),
});

// ❌ Awaiting executeAsync just to toast
const { executeAsync } = useAction(saveFoo);
const result = await executeAsync(input);
if (result?.data) toast.success(...); else toast.error(...);
```

### Don't extend legacy client-component pages — start converting them

When adding a new feature to a page that's still a client component using tRPC, don't add another client-side fetch alongside the existing ones. Instead: move the legacy client logic into a sibling `.client.tsx`, and make `page.tsx` a server component that fetches the new feature's data via domain queries and passes it down as props. Incremental conversion beats piling on more `useEffect` fetching.

### Controller field spreading

When using `Controller` with design system components, spread `field` first then override specific props.

### Submit buttons need `type="submit"`; the DS Button defaults to `type="button"`

The design-system `Button` always renders `<button type="button">` unless overridden — base-ui's `useButton` injects `type: 'button'` when `nativeButton: true` (the default). So:

- **Submit buttons**: must set `type="submit"` explicitly, otherwise they won't submit the form.
- **Cancel / secondary buttons inside a form**: do *not* need `type="button"` — the DS default already handles it. Don't flag a missing `type="button"` as a bug. Cancel handlers should still call `form.reset()` before closing.
- **Raw `<button>` elements** (not the DS component): the HTML default is `type="submit"` inside a form, so a raw cancel button *does* need `type="button"`.

### Use `.client.tsx` suffix for client components

Files with `"use client"` directive should use `.client.tsx` extension.

### `"use client"` is a JS-boundary marker, not an interactivity marker

A Server Component can render `<button type="button">` — the DOM is interactive, clicks just don't fire JS until something wires them. Mark a file `.client.tsx` only when you need React state, hooks, event handlers tied to functions, or browser-only APIs. `onClick={() => {}}` (no-op) is a smell — drop the wrapper and render the inert HTML from the server until a real handler shows up.

### Use `nuqs/server` for typed Server Component search params

Don't hand-roll `function isX(value: unknown): value is X` and `function parseY(value: unknown)` for each `searchParams` field. `nuqs/server` already provides typed parsers and a cache.

```typescript
// search-params.ts (sibling to page.tsx)
export const usersSearchParamsCache = createSearchParamsCache({
  search: parseAsString.withDefault(""),
  limit: parseAsStringLiteral(LIMIT_OPTIONS).withDefault(LIMIT_DEFAULT),
  cursor: parseAsInteger.withDefault(0),
});

// page.tsx
const { search, limit, cursor } = usersSearchParamsCache.parse(
  await props.searchParams,
);
```

Established convention — see `apps/admin/.../users/searchParams.ts`, `apps/company/.../reports/liability/search-params.tsx`.

### Parallelize independent top-level Server Component fetches with `Promise.all`

Auth, params, search params, feature flags, and unrelated domain queries don't depend on each other. Sequential `await`s waste round-trips.

```typescript
// ✅
const [user, params, searchParams, flags] = await Promise.all([
  getAuthedUser(),
  props.params,
  props.searchParams,
  getFlags(),
]);

// ❌ Sequential — adds round-trips for no reason
const user = await getAuthedUser();
const params = await props.params;
const searchParams = await props.searchParams;
const flags = await getFlags();
```

---

## Styling

### Use design tokens, not hardcoded colors

```typescript
// ❌ Hardcoded — doesn't support theming
className="bg-blue-600 border-neutral-200"

// ✅ Semantic tokens — adapts to theme/dark mode
className="bg-primary border-border"
```

Token mapping: selected/active → `border-primary bg-primary/10`, borders → `border-border`, hover → `hover:border-primary/50`.

### `rounded` is deprecated — use `rounded-sm`

Tailwind v4 remapped `rounded` to `rounded-sm`. The linter enforces this via `better-tailwindcss/no-deprecated-classes`.

### Use font utilities from `tw-config.css`, don't guess names

Available utilities: `font-page-title`, `font-statistic`, `font-headline-1`/`-2`/`-3`, `font-text-lg`/`-sm`/`-xs`, `font-numeric`/`-semibold`, `font-label`/`-semibold`, `font-badge`, `font-caption`, `font-link`/`-sm`/`-xs`. Check `utils/design-system/src/tw-config.css` when unsure — there is no `font-label-lg`, `font-heading`, etc.

### Use `gap` over margins between flex/grid children

```tsx
// ❌ Margins
<div className="flex"><div className="mr-2">A</div><div>B</div></div>

// ✅ Gap
<div className="flex gap-2"><div>A</div><div>B</div></div>
```

### Use `cn()` for conditional classes

Import `cn` from `@util/design-system` for conditional class combinations.

### Prefer Tailwind classes over inline styles

Use utility classes instead of inline `style` props with CSS variables.

### Outer wrappers should not have margins

Outer layout wrappers should rarely, if ever, have margins. Let content define spacing.

### Use named Tailwind width utilities, not arbitrary px values

Same principle as semantic color tokens and font utilities. `w-sm` (24rem = 384px), `w-md` (28rem = 448px), `w-2xl` (42rem = 672px), `max-w-5xl` (64rem = 1024px). Reach for `w-[NNNpx]` only when no scale step fits.

---

## Testing

### Error assertions: use `toStrictEqual(new Error(...))`

```typescript
// ✅ Preferred — tests message AND cause
expect(result.unwrapErr()).toStrictEqual(new Error("msg", { cause: mockError }));

// ❌ Incomplete
expect(result.unwrapErr().message).toBe("msg");
```

### Don't check `isErr()` separately

Just call `unwrapErr()` directly — it throws if the result is Ok.

### Include `cause` in error assertions

When a mutation wraps errors with `{ cause }`, the assertion must include it.

### Verify mocks before asserting results

Check `toHaveBeenCalledTimes` and `toHaveBeenCalledWith` before asserting on the returned value.

### Prefer per-test mocks over shared `beforeEach`

```typescript
// ✅ Isolated
it("does thing", () => {
  const clerkMock = mockDeep<ClerkClient>();
  // ...
});

// ❌ Shared mutable state
let clerkMock: DeepMockProxy<ClerkClient>;
beforeEach(() => { clerkMock = mockDeep<ClerkClient>(); });
```

### Use `mockInngest()` from `@util/event/test/helpers`

Don't manually `vi.spyOn(inngest, "send")`.

### Use `mockDeep` for external SDK clients

`vitest-mock-extended`'s `mockDeep<T>()` handles deep-proxy auto-mocking for any SDK with complex or overloaded types — `ClerkClient`, `S3Client`, Stripe, etc. Skip manual `vi.fn()` per method and avoid monkey-patching prototypes.

```typescript
import { mockDeep, type DeepMockProxy } from "vitest-mock-extended";

let s3Client: DeepMockProxy<S3Client>;
beforeEach(() => { s3Client = mockDeep<S3Client>(); });
// s3Client.send.mockResolvedValueOnce(...)
```

If the SDK's method signature has overloads that force `mockResolvedValueOnce(...)` into a void branch (e.g. `S3Client.send`'s callback overload), cast the mock value with a single `as never` and an eslint-disable comment naming the overload that resolved.

### Clean `beforeEach`

Use direct function references: `beforeEach(resetDB)` not `beforeEach(async () => { await resetDB(); })`.

### Type-annotate test variables instead of sprinkling `as const`

When test data needs to match a discriminated union or narrow type, annotate the variable with the type instead of adding `as const` on individual literals.

```typescript
// ✅ Type annotation — clean, consistent
const filters: BulkTransactionEventFilters = {
  type: "externalIds",
  connectionId: "conn_1",
  externalIds: ["ext_1"],
};

// ❌ Scattered as const — verbose, easy to miss one
const filters = {
  type: "externalIds" as const,
  connectionId: "conn_1",
  externalIds: ["ext_1"],
};
```

### Test non-trivial logic in domain functions

When a mutation or query has boundary translation logic (e.g., converting domain types to Prisma types, handling nullable JSON fields, relation connect/disconnect), write tests that exercise those paths specifically. Don't assume the happy-path test covers them.

```typescript
// ✅ Tests the null→DbNull conversion path
it("sets a JSON field to null", async () => {
  // seed with a populated value, update to null, verify SQL NULL
});

// ✅ Tests the relation connect/disconnect branches
it("connects a syncHistory by ID", ...);
it("disconnects a syncHistory when set to null", ...);
```

### Don't use Zod schemas for internal-only validation

If a function is only called from a server action/component that already validates, Zod is redundant. Use plain TypeScript defaults.

### Zod schema variable names are camelCase

87% of schema exports use camelCase (`analysisSpecSchema`, `createCompanyUserSchema`). A few PascalCase stragglers exist but shouldn't be copied.

### Don't test Inngest framework behavior

Inngest handles step ordering, retries, and error propagation — don't assert on them. Skip tests that check:

- Step names or execution order
- That `Promise.all` actually ran two `step.run` calls in parallel
- That an error from `step.run` halts subsequent steps
- Exact counts of `step.run` / `step.realtime.publish` calls

Test what *your* code does that reading it wouldn't reveal: cross-boundary payload contracts (e.g., realtime publish shapes consumed by the frontend), intentional design decisions that aren't obvious (e.g., best-effort publishes that swallow errors), and code in `onFailure` that doesn't run on the happy path.

---

## Domain Architecture

### Keep code in the correct domain package

- Partner-specific code → `@domain/partner`
- Company-specific code → `@domain/company`
- Shared Clerk logic → `@domain/auth` (takes `clerkOrganizationId` directly)
- Only Clerk-specific code belongs in `@domain/auth`

### Replace tRPC with direct domain queries

tRPC is legacy. Call domain queries directly in server components.

### Server actions are thin orchestrators

An action parses input, calls a domain query/mutation, and returns. Don't put `prisma.*` calls or `inngest.send()` inside an action file — extract to a tested domain function. This applies even to simple lookups (e.g., fetching a record to generate a signed URL): put the lookup in `@domain/<x>/queries/...` and have the action call it.

### Use relative imports within the same domain

```typescript
// ✅ Within @domain/registration
import { helper } from "./helper";

// ❌ Self-referencing package
import { helper } from "@domain/registration/helper";
```

### Consolidate similar queries

Prefer extending existing queries over creating new similar ones. Return a superset — consumers pick what they need.

### Single source of truth for constants

Don't duplicate constants across client/server. Consolidate to one location and import everywhere.

### Single per-key source for data shared across views

When the same keyed set of items renders across multiple views with view-specific decorations (e.g. an in-flight pending state and a terminal pass/fail state both rendering the same set of checks), put ALL per-key data in one constant and let each view ignore fields it doesn't need. Splitting into a "shared map" plus a "view-specific map" creates two sources of truth that drift. Extends "Return a superset — consumers pick what they need" from queries to constants. Reference: `IMPORT_CHECKS` in `apps/company/src/app/(protected)/[id]/integrations/[connectionId]/import/[sessionId]/import-check-row.tsx`, consumed by both pipeline-progress (in-flight) and rejected-view (terminal).

### Don't use Zod schemas where plain checks suffice

Co-located `*.schema.ts` files for action input validation. Runtime checks in mutations for critical validations (no Zod needed for internal calls).

### No barrel files in domain packages

Don't create `index.ts` files that re-export from a directory. Use wildcard exports in `package.json` instead. Consumers import specific files directly.

```json
// ✅ package.json
"exports": {
  "./mutations/*": "./src/mutations/*.ts",
  "./queries/*": "./src/queries/*.ts"
}

// ✅ Consumer
import { createFoo } from "@domain/foo/mutations/create-foo";

// ❌ Don't create src/mutations/index.ts barrel files
```

Empty directories don't need `.gitkeep` files either — the directory gets created naturally when the first file lands. See `@domain/onboarding` for the reference pattern.

---

## Background Jobs

### Separate orchestration from execution

Inngest functions should orchestrate (call mutations, coordinate steps). Business logic lives in domain mutations.

### Use event-driven, not cron, when an event exists

If an event already fires that should trigger the job, subscribe to it. Don't poll on a cron schedule.

### Step names use kebab-case

```typescript
step.invoke('get-audience-members-california', ...)
```

### Return useful data from steps

Return IDs/summaries from `step.run` so the Inngest UI shows meaningful output without drilling into logs.

### Use `step.run` for sync operations, `step.invoke` for other functions

Use `Promise.all` for concurrent `step.invoke` calls.

### `inngest.send()` stays outside try/catch

Codebase convention: Inngest sends are fire-and-forget, placed after DB operations but outside error handling.

### Co-locate Inngest-adjacent helpers under `background/`

Realtime channels, publishers, and other helpers whose only consumer is an Inngest function live in `background/` alongside the function, not at the domain root. A file at the domain root signals "domain-wide API"; nesting it in `background/` signals "orchestration-only" and keeps the public surface of the domain package focused.

### Destructure `logger` from handler args, not module-level `getLogger`

Inngest passes a context-aware logger into every handler (and `onFailure`). It auto-attaches `runId` / `functionId` / `eventId` and flows through Inngest's telemetry. Module-level `getLogger("fn-name")` skips all of that.

```typescript
// ✅ Preferred
async ({ event, step, logger }) => {
  logger.warn("something drifted", { ... });
}

// ❌ Module-level logger
const logger = getLogger("my-function");
```

### Orchestrator cleanup goes in `onFailure`, not an outer try/catch

When a function needs to mark a terminal-state record (e.g., `status: FAILED`) or publish a failure event on any error, put that in `onFailure` at the function-config level. The main handler stays as a straight-line happy path — no big try/catch wrapping the body.

`onFailure` receives the full step context, including `step.run`, `step.sendEvent`, and `step.realtime.publish`, so cleanup is durable. It fires on `NonRetriableError` or after retries exhaust — transient failures get retried before cleanup runs, so only real terminal failures write the DB.

Access the original event payload at `event.data.event.data` (failure events wrap the original).

```typescript
inngest.createFunction(
  {
    id: "my-fn",
    triggers: [...],
    onFailure: async ({ event, step, error }) => {
      const { companyId, recordId } = event.data.event.data;
      await step.run("mark-failed", async () => {
        (await updateRecord({ companyId, recordId, data: { status: FAILED } })).unwrap();
      });
    },
  },
  async ({ event, step, logger }) => {
    // happy path only
  },
);
```

### Poll external async jobs with capped exponential backoff, sized to the provider's worst case

When polling an external provider for job completion (report generation, bulk exports), don't use fixed-interval × fixed-count loops — the attempt ceiling silently encodes an assumption about how long the provider can take. Size the total window to the provider's realistic worst case (Amazon report generation can take hours) and back off exponentially with a cap so the tail doesn't overshoot. `step.sleep` is durable, so long sleeps cost nothing. If the provider offers a completion webhook, prefer it over polling entirely (Shopify bulk operations do this).

### Cap externally-generated files before ingesting them

When a sync pulls a provider-generated file (Shopify bulk operation, Amazon report), check its size or object count against an explicit maximum before processing, and fail the sync history with a user-readable reason. Precedent: `shopify/orders.ts` fails syncs above `MAX_ZAMP_OBJECT_COUNT` with "File too large". When the provider's metadata doesn't report a size, enforce the cap while streaming the download.

---

## Code Style

### No `let` in domain functions

If you need `let`, extract another function. Return directly from try/catch, conditionals, loops.

### Prefer named local functions over IIFEs for derived values

IIFEs (`const x = (() => { ... })();`) read as anonymous noise — the parens say nothing about what the block does. A named local function (or module-level helper) documents intent and is no harder to write. Put it inside the component when it captures closure variables, hoist to module scope otherwise.

```ts
// ❌ Anonymous IIFE — what does this block compute?
const latestSession = (() => {
  if (result === null) return null;
  if (result.isErr()) {
    captureException(result.error);
    return null;
  }
  return result.value;
})();

// ✅ Name says it: this resolves the latest session from a Result
function resolveLatestSession() {
  if (result === null) return null;
  if (result.isErr()) {
    captureException(result.error);
    return null;
  }
  return result.value;
}
const latestSession = resolveLatestSession();
```

### Try/catch extraction is a commitment, not a one-off

If an orchestrator function has multiple side-effecting steps and you extract one of them into a `Result`-returning helper, extract the rest too. Mixing inline try/catches with extracted helpers in the same function forces the reader to re-orient between two error-handling styles. Pick one shape per function.

```typescript
// ❌ Mixed: two extracted helpers + one inline try/catch
const rawResult = await loadTransformOutput({ ... });
if (rawResult.isErr()) return rawResult;
const validated = validateTransactions(rawResult.value);
if (validated.isErr()) return validated;
try {
  await s3Client.send(new PutObjectCommand({ ... }));
} catch (error) {
  return Err(new Error("Upload failed", { cause: error }));
}

// ✅ Symmetric: every step is a Result-returning helper
const rawResult = await loadTransformOutput({ ... });
if (rawResult.isErr()) return rawResult;
const validated = validateTransactions(rawResult.value);
if (validated.isErr()) return validated;
const uploadResult = await uploadZampCsv({ ... });
if (uploadResult.isErr()) return uploadResult;
```

### File names: kebab-case

`invite-partner-user.ts`, `create-company-user.schema.ts`.

### Import organization

External dependencies → internal domain imports → local imports.

### Use `type` keyword for type imports

```typescript
import type { ReactNode } from "react";
```

### Use `flatMap` to filter undefined

```typescript
// ✅ Type-safe
items.flatMap(x => x.value ? [x.value] : [])

// ❌ Needs type predicate
items.map(x => x.value).filter((v): v is string => v !== undefined)
```

### Use Prisma enum constants, not string literals

```typescript
// ✅ Type-safe — compile error if enum value is renamed
import { ConnectionStatus } from "@util/db/types";
status: ConnectionStatus.CONNECTED

// ❌ Silent breakage if enum value changes
import type { ConnectionStatus } from "@util/db/types";
status: "CONNECTED"
```

When referencing a Prisma enum value, import it as a value (not `type`-only) and use the constant. This applies to production code, tests, and factories.

### Don't reconstruct what the schema already discriminates

When a Zod discriminated union schema validates input, the parsed output already has the correct narrowed type. Destructure shared fields and rest-spread the variant-specific fields instead of manually rebuilding the union with a ternary.

```typescript
// ✅ Schema already discriminated — destructure and pass through
const { companyId, data, ...filters } = parsedInput;
await updateTransactions({ companyId, userId, data, filters });

// ❌ Redundant — manually reconstructing what the schema gave you
const filters = parsedInput.type === "externalIds"
  ? { type: "externalIds", connectionId: parsedInput.connectionId, externalIds: parsedInput.externalIds }
  : { type: "transactionFilters", filters: parsedInput.filters };
```

### No non-null assertions (`!`)

Use truthiness narrowing instead.

### Prefer direct lookups over fetch-all-and-filter

Use `getItem({ id })` instead of `getItems()` then `.find()`.

### Pass identifiers the operation needs

Accept `userId` directly, don't accept `membershipId` + lookup to extract userId.

### Naming should reflect behavior

A query named `getAll*` that filters should be `getActivityForEntity`, not `getAllActivity`.

### Use design-vocabulary names, not internal jargon

Internal product framings get renamed every quarter; names that mirror what the design system or end users call something survive. If Figma labels a row "File Check," the component is `FileCheckRow`, not `BigFourRow`.

### Drop redundant prefixes on solo props

A prop named `<state>Message` only earns its prefix if a sibling prop on the same component needs to be distinguished from it. `PendingImportCheckRow` has one message prop — name it `message`, since the component name already establishes the state. Reserve prefixed names (`passMessage`/`failMessage`) for siblings that must be told apart on the same component. Same principle at function-parameter level: prefer `setCount(n)` over `setCount(newCount)` when there's no other count in scope.

### Prefer `ts-pattern` `match()` over nested ternaries for status dispatch

When a component, page, or value branches on a status/state union with three or more cases, reach for `match(value).with(...).otherwise(...)` from `ts-pattern` instead of nested ternaries or if-chains. `P.union(...)` groups multiple variants under one handler. `.when(predicate, handler)` accepts type guards (e.g. `isLiveImportSessionStatus`). `.exhaustive()` for fixed enums where every case is handled; `.otherwise()` for an explicit fallback. Established across `transmission-table.client.tsx`, `your-subscription/page.tsx`, `economic-nexus/page.tsx`, and the import-session `page.tsx`.

### `Set.has()` for fixed-string-tuple membership tests

Idiomatic across the codebase (`FILING_ISSUE_ASSIGNEE_ROLES`, `EXCLUDED_BUSINESS_STRUCTURES`, `NON_RETRIABLE_STATUSES`, `ZAMP_PRODUCT_TAX_PATHS`). Cleaner than `.some((k) => k === value)`; widen the Set to `Set<string>` so type guards can accept `unknown`.

```typescript
const KEYS = ["a", "b", "c"] as const;
type Key = (typeof KEYS)[number];
const KEY_SET = new Set<string>(KEYS);

function isKey(value: unknown): value is Key {
  return typeof value === "string" && KEY_SET.has(value);
}
```

### PR discipline

Don't include unrelated changes. Don't push directly-related PR feedback into backlog tickets — fix it in the PR or create a follow-up ticket in the project.
