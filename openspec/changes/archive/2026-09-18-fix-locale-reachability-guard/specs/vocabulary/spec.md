# vocabulary Specification

## Purpose

Make the golden path speak the product's vocabulary and acknowledge the moment a result becomes company memory. The catalog that carries that vocabulary is only as trustworthy as the guard that reads it, so the guard has to hold in both directions.

## ADDED Requirements

### Requirement: The catalogs hold in both directions (VOC-05)

The locale guard SHALL fail when a translation key used in `apps/web` or in `packages/ui/src` is absent from the French and English catalogs, and SHALL fail when a key of the web catalog is reached by nothing in those sources or in the browser specs. A key reached through a dynamic family, through a whole-namespace read, or through a browser spec that reads the catalog directly SHALL count as reached. The final line the guard prints SHALL describe what it actually verified.

#### Scenario: A used key is absent from the catalogs

- **WHEN** a source calls `t('ideas.absent')` and no catalog holds that path
- **THEN** the guard reports the key together with the file that uses it
- **AND** the run fails

#### Scenario: A catalog key is reached by nothing

- **WHEN** a catalog holds a key under a namespace that no source uses, that no dynamic family covers and that no browser spec reads
- **THEN** the guard reports the key as unreachable
- **AND** the run fails

#### Scenario: A dynamic family stays accepted

- **WHEN** a source builds a key from a variable, as in `t(\`ideas.detail.roles.${role}\`)`, and the catalog holds keys under that prefix
- **THEN** those keys count as reached
- **AND** a namespace read whole through `tm('ideas.initiativeType')`, or through a browser spec that reads the catalog directly, counts as reached too
