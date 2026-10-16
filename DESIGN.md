# Design

## Product interface

Video Downloader Của Zu is a single-task desktop utility. Its screen uses a calm, light
neutral surface with a dark green primary action and system typography. The
main panel groups URL, destination, quality, and download controls in the
order users need them; progress and recovery remain visible on the same
screen. Keep native keyboard, focus, and file-picker behavior.

## Components and states

- Use standard Tk themed controls with one consistent spacing and button
  vocabulary.
- Keep the main action visually strongest; use accent color for actions and
  progress, not decoration.
- Show download status, measured progress, cancellation, and an actionable
  error without hiding the input flow.
- Respect system fonts and platform window conventions.

## Constraints

- The full task must fit in the first window on ordinary desktop displays.
- Keep controls understandable in Vietnamese and usable without a mouse.
- Do not imply that every URL is supported or that protected media can be
  downloaded.
