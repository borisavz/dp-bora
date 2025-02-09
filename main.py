from collections import deque
from typing import List, Set, Iterable

commutative = [True, True, False, False, False, True, False]

# TODO: support complex predicate check when tests are available
#       same applies to l-assoc and r-assoc as well
# def right_predicate_rejects_null(
#     left: "BinaryOperator",
#     right: "BinaryOperator"
# ):
#     return right.predicate_rejects_null
#
#
# def both_predicates_rejects_null(
#     left: "BinaryOperator",
#     right: "BinaryOperator"
# ):
#     return (
#         left.predicate_rejects_null
#         and right.predicate_rejects_null
#     )


# associative = [
#     [True, True, True, True, True, False, True],
#     [True, True, True, True, True, False, True],
#     [False, False, False, False, False, False, False],
#     [False, False, False, False, False, False, False],
#     [False, False, False, False, right_predicate_rejects_null, False, False],
#     [False, False, False, False, right_predicate_rejects_null, both_predicates_rejects_null, False],
#     [False, False, False, False, False, False, False]
# ]


associative = [
    [True, True, True, True, True, False, True],
    [True, True, True, True, True, False, True],
    [False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False]
]


def is_commutative(operator: "BinaryOperator"):
    return commutative[operator.operator_id]


def is_associative(left: "BinaryOperator", right: "BinaryOperator"):
    matrix_entry = associative[left.operator_id][right.operator_id]

    if isinstance(matrix_entry, bool):
        matrix_val = matrix_entry
    elif callable(matrix_entry):
        matrix_val = matrix_entry(left, right)
    else:
        raise Exception()

    if not matrix_val:
        return False

    return (
        not left.predicate_rels.intersection(right.right_rel_set)
        and not right.predicate_rels.intersection(left.left_rel_set)
    )


class Node:
    pass


class Relation(Node):
    def __init__(self, name: str):
        self.name = name

    # def __eq__(self, other):
    #     if not isinstance(other, Relation):
    #         return False
    #
    #     return self.name == other.name


class BinaryOperator(Node):
    def __init__(
        self,
        operator_id: int,
        left: Set[Node],
        right: Set[Node],
        predicate_rels: Set[Relation],
        predicate_rejects_null: bool = True,
        comment: str = ""
    ):
        self.operator_id = operator_id
        self.left = left
        self.right = right
        self.predicate_rels = predicate_rels
        self.predicate_rejects_null = predicate_rejects_null
        self.comment = comment

        self.top_parents = set()
        self.left_parents = set()
        self.right_parents = set()

        self.left_rel_set = set()
        self.right_rel_set = set()

        for l in left:
            if isinstance(l, Relation):
                self.left_rel_set.add(l)
            elif isinstance(l, BinaryOperator):
                l.left_parents.add(self)

                self.left_rel_set.update(l.left_rel_set)
                self.left_rel_set.update(l.right_rel_set)

        for r in right:
            if isinstance(r, Relation):
                self.right_rel_set.add(r)
            elif isinstance(r, BinaryOperator):
                r.right_parents.add(self)

                self.right_rel_set.update(r.left_rel_set)
                self.right_rel_set.update(r.right_rel_set)

    def add_left_child(self, node):
        # if any(
        #     isinstance(l, BinaryOperator)
        #     and l.operator_id == node.operator_id
        #     and l.left_rel_set == node.left_rel_set
        #     and l.right_rel_set == node.right_rel_set
        #     for l
        #     in self.left
        # ):
        #     return

        self.left.add(node)

        if isinstance(node, BinaryOperator):
            node.left_parents.add(self)

    def add_right_child(self, node):
        # TODO: prevent adding duplicate
        self.right.add(node)

        if isinstance(node, BinaryOperator):
            node.right_parents.add(self)

    @staticmethod
    def inner_join(left_node: Node, right_node: Node, predicate_rels: Set[Relation]):
        return BinaryOperator(
            operator_id=0,
            left={left_node},
            right={right_node},
            predicate_rels=set(predicate_rels),
            comment="original"
        )


class Result(Node):
    def __init__(self, children: Set[Node]):
        self.children = children

        for c in children:
            if isinstance(c, BinaryOperator):
                c.top_parents.add(self)

    def add_child(self, node: Node):
        # TODO: prevent adding duplicate
        self.children.add(node)

        if isinstance(node, BinaryOperator):
            node.top_parents.add(self)

    @staticmethod
    def create(child_node: Node):
        return Result(children={child_node})


def generate_search_space(query: Result):
    worklist = generate_initial_worklist(query.children)
    equivalent_nodes = generate_initial_equivalent_nodes(worklist)

    iter_count = 0

    while True:
        new_nodes = iterate_worklist(worklist, equivalent_nodes)

        if new_nodes:
            worklist = new_nodes
        else:
            break

        iter_count += 1


def generate_initial_worklist(query: Iterable[Node]):
    result = []

    queue = deque(query)

    while queue:
        node = queue.popleft()

        if not isinstance(node, BinaryOperator):
            continue

        result.append(node)

        for ln in node.left:
            if isinstance(ln, BinaryOperator):
                queue.append(ln)

        for rn in node.right:
            if isinstance(rn, BinaryOperator):
                queue.append(rn)


    return result


def generate_initial_equivalent_nodes(nodes: List[BinaryOperator]):
    equivalent_nodes = dict()

    for n in nodes:
        key = (
            n.operator_id,
            frozenset(n.left_rel_set),
            frozenset(n.right_rel_set)
        )

        equivalent_nodes[key] = n

    return equivalent_nodes


def equivalent_node_exists(equivalent_nodes, operator_id, left_rel_set, right_rel_set):
    key = (
        operator_id,
        frozenset(left_rel_set),
        frozenset(right_rel_set)
    )

    return key in equivalent_nodes


def get_equivalent_node_if_exists(equivalent_nodes, operator_id, left_rel_set, right_rel_set):
    key = (
        operator_id,
        frozenset(left_rel_set),
        frozenset(right_rel_set)
    )

    if key in equivalent_nodes:
        return equivalent_nodes[key]
    else:
        return None


def add_equivalent_node(equivalent_nodes, node):
    if not isinstance(node, BinaryOperator):
        return

    key = (
        node.operator_id,
        frozenset(node.left_rel_set),
        frozenset(node.right_rel_set)
    )

    # assert key not in equivalent_nodes

    if key in equivalent_nodes:
        b1 = equivalent_nodes[key]
        assert False

    equivalent_nodes[key] = node


def iterate_worklist(worklist: List[BinaryOperator], equivalent_nodes):
    new_nodes = []

    attempt_transformations = [
        attempt_commutativity,
        attempt_associativity_ltr_child,
        attempt_associativity_ltr_parent
    ]

    for w in worklist:
        for attempt_func in attempt_transformations:
            trans_new_nodes = attempt_func(w, equivalent_nodes)
            new_nodes.extend(trans_new_nodes)

    return new_nodes


def attempt_commutativity(node: BinaryOperator, equivalent_nodes):
    new_nodes = []

    if (
        is_commutative(node)
        and not equivalent_node_exists(
            equivalent_nodes,
            node.operator_id,
            node.right_rel_set,
            node.left_rel_set
        )
    ):

        new_node = BinaryOperator(
            operator_id=node.operator_id,
            left=node.right,
            right=node.left,
            predicate_rels=node.predicate_rels,
            comment="comm new node"
        )

        for t in node.top_parents:
            t.add_child(new_node)

        for l in node.left_parents:
            l.add_left_child(new_node)

        for r in node.right_parents:
            r.add_right_child(new_node)

        add_equivalent_node(equivalent_nodes, new_node)

        new_nodes.append(new_node)

    return new_nodes


def attempt_associativity_ltr_child(node: BinaryOperator, equivalent_nodes):
    new_nodes = []

    old_parent_nodes_for_update = []

    for l in node.left:
        if not isinstance(l, BinaryOperator):
            continue

        if not is_associative(l, node):
            continue

        existing_child_node = get_equivalent_node_if_exists(
            equivalent_nodes,
            node.operator_id,
            l.right_rel_set,
            node.right_rel_set
        )

        if existing_child_node:
            child_node = existing_child_node
        else:
            child_node = BinaryOperator(
                operator_id=node.operator_id,
                left=l.right,
                right=node.right,
                predicate_rels=node.predicate_rels,
                comment="assoc ch node"
            )

            add_equivalent_node(equivalent_nodes, child_node)
            new_nodes.append(child_node)

        existing_parent_node = get_equivalent_node_if_exists(
            equivalent_nodes,
            l.operator_id,
            l.left_rel_set,
            l.right_rel_set.union(node.right_rel_set)
        )

        if existing_parent_node:
            parent_node = existing_parent_node
        else:
            parent_node = BinaryOperator(
                operator_id=l.operator_id,
                left=l.left,
                right={child_node},
                predicate_rels=l.predicate_rels,
                comment="assoc p node"
            )

            add_equivalent_node(equivalent_nodes, parent_node)
            new_nodes.append(parent_node)

        for t in node.top_parents:
            t.add_child(parent_node)

        for l in node.left_parents:
            l.add_left_child(parent_node)

        for r in node.right_parents:
            r.add_right_child(parent_node)

    return new_nodes


def attempt_associativity_ltr_parent(node: BinaryOperator, equivalent_nodes):
    return []


if __name__ == '__main__':
    rel_a = Relation("a")
    rel_b = Relation("b")
    rel_c = Relation("c")
    rel_d = Relation("d")
    rel_e = Relation("e")
    rel_f = Relation("f")
    rel_g = Relation("g")
    rel_h = Relation("h")

    # query = Result.create(
    #     BinaryOperator.inner_join(
    #         BinaryOperator.inner_join(
    #             BinaryOperator.inner_join(
    #                 rel_a,
    #                 rel_b,
    #                 {rel_a, rel_b}
    #             ),
    #             BinaryOperator.inner_join(
    #                 rel_c,
    #                 rel_d,
    #                 {rel_c, rel_d}
    #             ),
    #             {rel_a, rel_c}
    #         ),
    #         BinaryOperator.inner_join(
    #             BinaryOperator.inner_join(
    #                 rel_e,
    #                 rel_f,
    #                 {rel_e, rel_f}
    #             ),
    #             BinaryOperator.inner_join(
    #                 rel_g,
    #                 rel_h,
    #                 {rel_g, rel_h}
    #             ),
    #             {rel_e, rel_g}
    #         ),
    #         {rel_a, rel_h}
    #     )
    # )

    query = Result.create(
        BinaryOperator.inner_join(
            BinaryOperator.inner_join(
                rel_a,
                rel_b,
                {rel_a, rel_b}
            ),
            rel_c,
            {rel_b, rel_c}
        )
    )

    generate_search_space(query)

    pass