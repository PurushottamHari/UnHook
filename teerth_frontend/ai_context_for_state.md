# Dashboard Article Widget - UX Requirements & Implementation Notes

## Overview
This document captures the UX requirements and implementation details for the article interaction widgets on the dashboard. These requirements were established through iterative UX experimentation and should be referenced when implementing or modifying the article interaction features.

## Dashboard Article Cards (`ExpandableArticleCard`)

### Visible Action Buttons (Desktop Only)
**Location**: Bottom-right corner of each article card

**Buttons**:
1. **Save for Later** (Bookmark icon)
   - Always visible on desktop (`hidden md:block`)
   - Hidden on mobile (available in 3-dot menu)
   - Opacity: 75% default, 100% on hover
   - Color: `text-amber-600 dark:text-amber-700`
   - State distinction: Filled icon when saved, outline when not saved

2. **3-Dot Menu** (More options)
   - Always visible (both mobile and desktop)
   - Opacity: 75% default on desktop, 100% on hover
   - On mobile: Has background/chip styling for visibility
   - On desktop: No background, transparent

### 3-Dot Menu Contents
**All actions available in the menu**:
1. Mark as Read / Mark as Unread
2. Save for Later / Remove from Saved
3. Like / Unlike
4. Dislike / Remove Dislike
5. Report / Remove Report

**Mobile Behavior**:
- Menu appears as a compact popover above the button
- Fixed width: `w-56` on mobile, `w-48` on desktop
- Scrollable if content exceeds `max-h-[70vh]`
- Positioned above the button (not covering the article)
- Each menu item has proper spacing: `px-4 py-3` with `gap-3`
- Icons are `w-5 h-5` for consistency
- Text size: `text-sm` for readability

**Desktop Behavior**:
- Dropdown appears above the 3-dot button
- Same compact design as mobile
- All items visible without scrolling (typically)

### Visual Design Principles

**Icon Styling**:
- Use outline icons for inactive states
- Use filled icons for active states
- Color: `text-amber-600 dark:text-amber-700` (NOT grey)
- Opacity: 75% default, 100% on hover
- No background, no chip, no color block on desktop
- Size: `w-5 h-5` consistently

**Positioning**:
- Bottom-right corner: `absolute bottom-4 right-4`
- Content area has `pb-16` padding to prevent overlap
- Buttons don't interfere with article content or "Read more" button

**State Management**:
- All actions are toggleable/reversible
- State persists in localStorage (mock implementation)
- Real-time updates via custom events
- State distinction clearly visible (filled vs outline icons)

## Article Reading Page

### Floating Action Bar (`ArticleActionBar`)
**Location**: Fixed at bottom of viewport

**Actions** (all visible):
1. Like / Unlike
2. Save for Later / Remove from Saved
3. Mark as Read / Mark as Unread
4. Dislike / Remove Dislike
5. Report / Remove Report

**Auto-Hide Behavior**:
- **Shows when**:
  - Page first loads (at top of article)
  - User scrolls to bottom (within last 10% or 100px from bottom)
  - User manually triggers via "Show Actions" button
  
- **Hides when**:
  - User scrolls down past 200px (reading the article)
  - Only hides when scrolling down (not when scrolling up)
  
- **Show Actions Button**:
  - Appears in bottom-right corner when action bar is hidden
  - Amber button with 3-dot icon
  - Clicking it shows the action bar for 5 seconds, then auto-hides again if user scrolls

**Design**:
- Sticky at bottom: `fixed bottom-0`
- Smooth slide animation: `translate-y-0` (visible) / `translate-y-full` (hidden)
- Transition: `duration-300 ease-in-out`
- Doesn't interrupt reading experience - auto-hides during reading
- All icons show state (filled when active)
- Article content has `pb-24` padding to prevent overlap

## Modals (Dislike & Report)

### Positioning
- **CRITICAL**: Use React Portal to render at `document.body` level
- This prevents positioning issues with parent containers
- z-index: `z-[9999]` to appear above all content
- Centered on viewport: `fixed inset-0 flex items-center justify-center`
- Mobile: Use `overflow-y-auto` with inner wrapper for proper centering

### Dismissal
- Backdrop click closes modal (with `cursor-pointer` indicator)
- Close button (X) in top-right corner
- Cancel button in form
- All three methods should work reliably

### Mobile Alignment
- Use nested flex container for proper vertical centering on mobile
- Outer: `overflow-y-auto` for scrollable backdrop
- Inner: `min-h-full` with `py-4` for proper centering
- Prevents modal from being cut off or shifted below viewport

## Dashboard Sections

### Article Organization
Articles are automatically organized into sections based on interaction state:

1. **Main Articles** (default view)
   - Unread, unliked, unreported articles
   - Always visible

2. **Read Articles** (collapsible)
   - Articles marked as read
   - Collapsed by default
   - Shows count: `(n)`

3. **Disliked Articles** (collapsible)
   - Articles that have been disliked
   - Collapsed by default
   - Shows count: `(n)`

4. **Reported Articles** (collapsible)
   - Articles that have been reported
   - Collapsed by default
   - Shows count: `(n)`

**Priority**: Disliked > Reported > Read > Main
- If an article is disliked, it goes to "Disliked" section
- If reported (but not disliked), goes to "Reported" section
- If read (but not disliked/reported), goes to "Read" section
- Otherwise, stays in "Main" section

### Section Component (`ArticleSection`)
- Collapsible with chevron icon
- Shows article count
- Icon indicator for section type
- Smooth expand/collapse animation

## State Management

### Mock Service (`article-interaction-service.ts`)
Currently uses localStorage for state persistence:
- Key format: `user_{userId}`
- Stores all interaction states per article
- Dispatches custom events for real-time UI updates

**States tracked**:
- `isRead`: boolean
- `isSaved`: boolean
- `isLiked`: boolean
- `isDisliked`: boolean (with optional reason)
- `isReported`: boolean (with optional reasons array)

**All actions are toggleable**:
- Can mark as read, then unread
- Can save, then unsave
- Can like, then unlike
- Can dislike, then remove dislike (with confirmation)
- Can report, then remove report (with confirmation)

### Future Backend Integration
When implementing backend:
- Replace localStorage calls with API calls
- Service structure is ready for easy replacement
- Maintain same function signatures
- Keep state management pattern consistent

## Key UX Principles

1. **Non-intrusive**: Actions don't clutter the reading experience
2. **Discoverable**: Actions are accessible but subtle
3. **Reversible**: All actions can be undone
4. **Stateful**: Clear visual distinction between active/inactive states
5. **Responsive**: Different UX patterns for mobile vs desktop
6. **Accessible**: Proper ARIA labels and keyboard navigation

## Mobile-Specific Considerations

1. **3-dot menu only**: On mobile, only show 3-dot menu (no standalone buttons)
2. **Compact popover**: Menu should be small, readable, and not cover article
3. **Touch-friendly**: Larger touch targets (`py-3` minimum)
4. **Scrollable**: Menu can scroll if needed
5. **Easy dismissal**: Click outside or on backdrop to close

## Desktop-Specific Considerations

1. **Quick actions visible**: Save for Later button always visible
2. **Subtle styling**: 75% opacity, no backgrounds
3. **Hover states**: Full opacity on hover
4. **Dropdown menu**: Compact, appears above button

## Important Notes

- **Modal positioning bug**: Always use React Portal for modals to prevent positioning issues
- **Mobile centering**: Use nested flex containers for proper vertical centering
- **State updates**: Dashboard sections update in real-time via custom events
- **Icon consistency**: All icons should be `w-5 h-5` with amber colors
- **No grey icons**: Use amber-600/700, not grey, for better visibility while staying subtle

## Testing Checklist

- [ ] Modals appear centered on screen (not relative to parent)
- [ ] Modals are easily dismissible (backdrop, X button, Cancel)
- [ ] Mobile menu doesn't cover article content
- [ ] Desktop shows Save for Later + 3-dot menu
- [ ] Mobile shows only 3-dot menu
- [ ] All actions are toggleable
- [ ] State is visually distinct (filled vs outline icons)
- [ ] Dashboard sections update when interactions change
- [ ] Icons are subtle but visible (75% opacity, amber color)

