# DP Bora - transformation-based optimizers strike again!

## Introduction

DP Bora is a novel algorithm for optimization of SQL queries.
It is closely based on DP SUBE, so readers are advised to read the DP SUBE
paper first. DP Bora dispoves two thesis present in DP SUBE paper:

1. Transformation-based optimizers are not efficient because they consume a lot of memory
2. Transformation-based optimizers generate exponential number of duplicates

Current limitations are overcome by innovative data structure called **query hypertree**,
which describes complete combinatorial search space in a compact and duplicate-free representation
suitable for use in both top-down (memoization) and bottom-up (dynamic programming) optimizers.

DP Bora enumerates complete search space (all possible bushy trees) and supports arbitrary joins and arbitrary predicates.
Extension of DP SUBE is that arbitrary transformations are also supported by the algorithm and it's main
internal data structure.

DP Bora comes with a reference implementation to alleviate all possible ambiguities present in the text
and to provide additional information necessary for production-grade implementation.

Author strongly believes that complex (i.e. hard to understand and truly prove) mathematical proofs
and absence of reference implementations lead to general disregard to computer science from
industry-oriented team members. DP Bora aims to overcome discrepancy between theory and practice.

## Introduction to SQL query optimization

## Query hypertree

## Algorithm outline

1. Canonical query tree is constructed directly from the SQL query
2. All initially present operator nodes are addded to the worklist
3. For every node in the worklist, every possible transformation is attempted
4. Transformation output is stored in query hypertree as an alternative path that does not affect originally present paths
5. After performing all possible transformations, a node is removed from the worklist
6. All newly created (i.e. transformed) nodes are added to the worklist
7. If a transformation attemts to create a node that is present, existing equivalent node is reused
8. Nodes are considered equivalent if they have the same operator and same input relations on the left side and on the right side
9. When worklist becomes empty, complete search space was enumerated
10. Query hypertree is used to calculate the cheapest path using either memoization or dynamic programming

## Supported transformations and node equivalence

DP Bora supports all transformations described in the DP SUBE paper: *commutativity*, *associativity*,
*l-asscom* and *r-asscom*. DP Bora uses the same matrices and predicates from DP SUBE paper to
check whether a transformation can be applied to a subtree. DP Bora does not use *conflict representation set* calculation.

Instead, transformations are applied (if possible) and added as possible alternative paths in the
**query hypertree**. Instead of resolving conflicts, DP Bora attemts all possible transformations
over all possible paths using duplicate-prevention strategy based on operator equivalence.

Separate map-based structure holds pairs of tuples `(operator, left_relation_set, right_relation_set)` and **query hypernodes**.
When a transformation attemts to create a node, `equivalent_nodes` map is searched for existence of
the needed node. If needed node exists, it is picked. Otherwise, a new node is constructed and added
to the `equivalent_nodes` map. Left and right inputs are stored as sets, so adding duplicate
paths is prevented as well. Using reference/memory address equivalence in sets is sufficient,
as duplicate construction (previous step) is prevented using a robust approach.
