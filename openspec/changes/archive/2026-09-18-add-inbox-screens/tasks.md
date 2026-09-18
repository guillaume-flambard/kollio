# Tasks

## 1. Vocabulary and route

- [x] 1.1 Add the inbox keys to both catalogs: the title and the intro, the four section titles with their intros, the six labels that say what waits, an empty line per section, the honest note about the section the inbox cannot answer, the remaining count and the read failure, plus the Inbox entry in the navigation.
- [x] 1.2 Add the Nitro proxy for the inbox read, carrying the optional limit only when it is a number.

## 2. The inbox screen

- [x] 2.1 Render `/workspace` as the Decision Inbox and read the four sections the API answers.
- [x] 2.2 Make every entry name what waits (the kind of work, the space question, its detail when there is one) and lead to the space and the section where it can be acted on.
- [x] 2.3 State each section's bound with the number of entries left beyond the ones it shows.
- [x] 2.4 Let an empty section say it is empty, and an inbox with nothing waiting say so once instead of fabricating work.
- [x] 2.5 Name the section the inbox cannot answer yet with the reason, instead of rendering an empty list under it.
- [x] 2.6 Keep the heading and the intro rendered when the read fails, and show the failure as an alert.

## 3. Rehome the space list and the navigation

- [x] 3.1 Move the decision space list to `/workspace/decision-spaces` unchanged and point its browser spec at the new route.
- [x] 3.2 Give the navigation four entries with the inbox first, each one marking its own active area, leaving Initiatives and Settings as they were.

## 4. Browser evidence

- [x] 4.1 Add the inbox browser spec, red then green, covering the four sections, the link each entry carries, the remaining count, the per-section empty lines, the global empty state, the note about the unanswered section, the read failure and the way to the space list.
- [x] 4.2 Keep the space list spec and the navigation assertions green with the moved route and the fourth entry.

## 5. Verification

- [x] 5.1 Run the linter and the type checker.
- [x] 5.2 Run the locale gate, the design token gate and the UX coverage gate.
- [x] 5.3 Run the whole browser suite and the production build.
- [x] 5.4 Validate the change with the OpenSpec CLI.
