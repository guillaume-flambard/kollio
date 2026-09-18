# Tasks — add-learning-screens

## 1. Vocabulary and proxies

- [x] 1.1 Add the section's words to both catalogs (`decisionSpaces.learning.*`: the two
      statuses, the two groups, the lesson text, the descent fields, the confirm and save
      actions, and the two notes that say a person confirms a lesson and that a draft is
      kept), and record the vocabulary in `apps/web/CONTEXT.md`.
- [x] 1.2 Add the Nitro proxy that lists a Space's lessons, keeping the write path on the
      existing experiment learning proxy.

## 2. The Learning section

- [x] 2.1 List the Space's lessons, each with its status told apart in words and its text.
- [x] 2.2 Let a proposed lesson's text be edited and confirmed, and say so when the write is
      refused.
- [x] 2.3 Let an edit be saved without confirming, and say that the lesson stays a kept
      draft: nothing is deleted.
- [x] 2.4 Show a confirmed lesson with its whole descent: the outcome it came from, the
      experiment that produced it, the initiative it belongs to, and who confirmed it.
- [x] 2.5 Render the section's heading and its intro unconditionally, with an honest empty
      state, distinct empty states per group, and error roles for a read or a write that
      fails.

## 3. Browser evidence

- [x] 3.1 Add failing browser specs covering the empty state, a proposed lesson, confirming,
      saving a draft, a confirmed lesson with its descent, the refusal path, the read
      failure and the absence of any score or verdict.
- [x] 3.2 Carry them to green while keeping the shell's section test intact, then the whole
      browser suite.

## 4. Documentation

- [x] 4.1 Write the capability delta for `learning-screens`.
- [x] 4.2 Record the scenario-to-test evidence, the boundaries and what is deferred in
      `acceptance.md`.

## 5. Verification

- [x] 5.1 Lint and typecheck.
- [x] 5.2 Locale gate, design-token gate and UX-coverage gate.
- [x] 5.3 Browser suite and production build.
- [x] 5.4 Validate the change with the OpenSpec CLI.
