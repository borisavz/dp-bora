from collections import deque
from typing import List


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

    pass


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
        left: List[Node],
        right: List[Node],
        predicate_rejects_null: bool = True
    ):
        self.operator_id = operator_id
        self.left = left
        self.right = right
        self.predicate_rejects_null = predicate_rejects_null

        self.left_rel_set = set()
        self.right_rel_set = set()

        for l in left:
            if isinstance(l, Relation):
                self.left_rel_set.add(l)
            elif isinstance(l, BinaryOperator):
                self.left_rel_set.update(l.left_rel_set)
                self.left_rel_set.update(l.right_rel_set)
            else:
                raise Exception()

        for r in right:
            if isinstance(r, Relation):
                self.right_rel_set.add(r)
            elif isinstance(r, BinaryOperator):
                self.right_rel_set.update(r.left_rel_set)
                self.right_rel_set.update(r.right_rel_set)
            else:
                raise Exception()


def generate_search_space(query: BinaryOperator):
    worklist = generate_initial_worklist(query)

    while True:
        new_nodes = iterate_worklist(worklist)

        if new_nodes:
            worklist = new_nodes
        else:
            break


def generate_initial_worklist(query: BinaryOperator):
    result = []

    queue = deque([query])

    while queue:
        node = queue.popleft()

        result.append(node)

        for ln in node.left:
            if isinstance(ln, BinaryOperator):
                queue.append(ln)

        for rn in node.right:
            if isinstance(rn, BinaryOperator):
                queue.append(rn)


    return result


def iterate_worklist(worklist: List[BinaryOperator]):
    new_nodes = []

    for w in worklist:

        pass

    return new_nodes


if __name__ == '__main__':
    query = BinaryOperator(
        operator_id=0,
        left=[BinaryOperator(
            operator_id=0,
            left=[Relation("a")],
            right=[Relation("b")]
        )],
        right=[Relation("c")]
    )

    generate_search_space(query)

    pass