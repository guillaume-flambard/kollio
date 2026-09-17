## 1. Vocabulary and routes

- [x] 1.1 Add the `decisionSpaces.converge.*` keys to both locales and record Converge, Relation and Cluster in `apps/web/CONTEXT.md`.
- [x] 1.2 Add the seven Nitro proxies for the `converge` operations, refusing a missing or blank required field before the request reaches the API.

## 2. The Converge section

- [x] 2.1 Read the map and render every confirmed Contribution with the kind it carries and the group a human placed it in, saying plainly when it is not grouped.
- [x] 2.2 Let a member assert a Relation between two Contributions with one of the eight kinds, and list every Relation with its kind and its two ends.
- [x] 2.3 Let a member delete a Relation.
- [x] 2.4 Let a member create a Cluster, add a Contribution to it, remove one, and delete the Cluster, a Contribution living in one Cluster at a time.
- [x] 2.5 Say the map is empty and point at Explore when the Space holds no confirmed Contribution.

## 3. Browser evidence

- [x] 3.1 Add failing browser specs for the map, the Relations and the Clusters, including the empty Space and a load that fails.
- [x] 3.2 Carry them to green while keeping the two `decision-spaces.spec.ts` scenarios that assert the title and the body of the Converge section passing.

## 4. Documentation

- [x] 4.1 Write the `converge-screens` spec delta.
- [x] 4.2 Record the scenario-to-test table, the boundaries and the deferred work in `acceptance.md`.

## 5. Verification

- [x] 5.1 Run lint and type checking.
- [x] 5.2 Run the locale gate, the design-token gate and the UX coverage gate.
- [x] 5.3 Run the browser suite and the production build.
- [x] 5.4 Run `openspec validate add-converge-screens`.
