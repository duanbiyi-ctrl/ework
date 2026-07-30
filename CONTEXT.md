# Item Domain LDM Documentation

This context defines the vocabulary for Item-domain logical and source-model
documentation.

## Language

**LDM page**:
A reader-facing documentation entry for a governed logical entity or a
source-model structure, named for the data concept it represents.
_Avoid_: Keyspace page, docset page

**LDM name**:
An UpperCamelCase page identity followed by ` LDM`, such as `ItemRoot LDM`.
_Avoid_: Space-free LDM suffixes

**NuDocument docset**:
A physical NuData/MonStor collection with a persisted JSON schema and key
shape. Its raw name and fields remain visible in an LDM page's Overview and
schema.
_Avoid_: LDM field, relational table

**NuDoc JSON field**:
The exact persisted JSON property name defined by the NuDocument schema,
including abbreviated aliases. Embedded values remain their declared NuDoc
object or scalar type and are not flattened into derived paths.
_Avoid_: Normalized LDM field, flattened JSON path
