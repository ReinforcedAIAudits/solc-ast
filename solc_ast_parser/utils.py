from collections import deque
import json
import random
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import solcx

from solc_ast_parser.models import ast_models
from solc_ast_parser.models.ast_models import SourceUnit
from solc_ast_parser.models.base_ast_models import Comment, MultilineComment, NodeType


def compile_contract_from_source(source: str):
    suggested_version = solcx.install.select_pragma_version(
        source, solcx.get_installable_solc_versions()
    )
    json_compiled = solcx.compile_source(source, solc_version=suggested_version)
    return json_compiled[list(json_compiled.keys())[0]]["ast"]


def compile_contract_with_standart_input(
    source: str, contract_file_name: str = "example.sol"
):
    suggested_version = solcx.install.select_pragma_version(
        source, solcx.get_installable_solc_versions()
    )
    json_compiled = solcx.compile_standard(
        create_standard_solidity_input(source, contract_file_name),
        solc_version=suggested_version,
    )["sources"]
    return json_compiled[list(json_compiled.keys())[0]]["ast"]


def create_ast_from_source(source: str) -> SourceUnit:
    ast = compile_contract_from_source(source)
    return SourceUnit(**ast)


def create_ast_with_standart_input(
    source: str, contract_file_name: str = "example.sol"
) -> SourceUnit:
    ast = compile_contract_with_standart_input(source, contract_file_name)
    return SourceUnit(**ast)


def traverse_ast(
    node: ast_models.ASTNode,
    visitor: Callable[[Any, Optional[ast_models.ASTNode]], None],
    parent: Optional[ast_models.ASTNode] = None,
) -> None:
    """Traverse AST and apply visitor function to each node."""
    if node is None:
        return
    with open("node.txt", "a") as f:
        f.write(f"{node}\n") if node.id == 136 else None
    visitor(node, parent)

    for field_name, field in node.model_fields.items():
        value = getattr(node, field_name)

        if isinstance(value, list):
            for item in value:
                if hasattr(item, "__fields__") and hasattr(item, "node_type"):
                    traverse_ast(item, visitor, node)
        elif hasattr(value, "__fields__") and hasattr(value, "node_type"):
            traverse_ast(value, visitor, node)


def replace_node(ast_node: Any, target_id: int, replacement_node: Any) -> bool:
    if hasattr(ast_node, "id") and ast_node.id == target_id:
        return False

    stack = deque([(ast_node, None, None)])

    while stack:
        current_node, parent_field, list_index = stack.popleft()

        for field_name, field_value in current_node.__dict__.items():
            if isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if hasattr(item, "id") and item.id == target_id:
                        field_value[i] = replacement_node
                        return True
                    elif hasattr(item, "__dict__"):
                        stack.append((item, field_name, i))

            elif hasattr(field_value, "__dict__"):
                if hasattr(field_value, "id") and field_value.id == target_id:
                    setattr(current_node, field_name, replacement_node)
                    return True
                stack.append((field_value, field_name, None))

    return False


def create_standard_solidity_input(contract_content: str, contract_name: str) -> Dict:
    return {
        "language": "Solidity",
        "sources": {contract_name: {"content": contract_content}},
        "settings": {
            "stopAfter": "parsing",
            "outputSelection": {"*": {"": ["ast"]}},
        },
    }


def find_comments(source: str) -> List[Union[Comment, MultilineComment]]:
    comments = []

    for match in re.finditer(r"(.*)(\/\/.*?(?=\n|$))", source):
        comments.append(
            create_comment_node(
                match.start() + len(match.group(1)) - 2,
                match.group(2).strip("/ "),
                False,
                match.group(1).strip() == "",
            )
        )

    for match in re.finditer(r"/\*.*?\*/", source, re.DOTALL):
        comments.append(create_comment_node(match.start(), match.group(), True))

    return sorted(comments, key=lambda x: x.src.split(":")[0])


def create_comment_node(
    start: int, text: str, is_multiline: bool = False, is_pure: bool = True
) -> Comment:
    if is_multiline:
        return MultilineComment(
            src=f"{start}:{len(text)}:0",
            text=text,
            id=random.randint(0, 1000000),
            nodeType=NodeType.MULTILINE_COMMENT,
        )
    return Comment(
        src=f"{start}:{len(text)}:0",
        text=text,
        id=random.randint(0, 1000000),
        nodeType=NodeType.MULTILINE_COMMENT if is_multiline else NodeType.COMMENT,
        isPure=is_pure,
    )


def insert_comments_into_ast(source_code: str, ast: SourceUnit) -> SourceUnit:
    comments = find_comments(source_code)
    return insert_nodes_into_ast(ast, comments)


def insert_node_into_node(
    node: ast_models.ASTNode,
    parent_node: ast_models.ASTNode,
    new_node: ast_models.ASTNode,
) -> ast_models.ASTNode:
    if node == new_node:
        return parent_node

    if not parent_node:
        if node.node_type == NodeType.SOURCE_UNIT:
            node.nodes.insert(0, new_node)
        return node

    if new_node.node_type == NodeType.COMMENT and not new_node.is_pure:
        node.comment = new_node
        return node

    if parent_node.node_type in (NodeType.SOURCE_UNIT, NodeType.CONTRACT_DEFINITION):
        parent_node.nodes.insert(parent_node.nodes.index(node), new_node)
    elif parent_node.node_type == NodeType.BLOCK:
        parent_node.statements.insert(parent_node.statements.index(node), new_node)
    else:
        parent_node.comment = new_node

    return parent_node


def insert_nodes_into_ast(ast: SourceUnit, nodes: List[Comment]) -> SourceUnit:
    for node in nodes:
        min_distance = float("inf")
        closest_node = None
        parent_node = None

        def find_closest_node(
            current_node: ast_models.ASTNode, parent: Optional[ast_models.ASTNode]
        ) -> None:
            nonlocal min_distance, closest_node, parent_node
            start = int(current_node.src.split(":")[0])
            if isinstance(node, Comment) and not node.is_pure:
                start = int(current_node.src.split(":")[0]) + int(
                    current_node.src.split(":")[1]
                )
            distance = start - int(node.src.split(":")[0])
            if 0 <= distance < min_distance:
                min_distance = distance
                closest_node = current_node
                parent_node = parent

        traverse_ast(ast, find_closest_node)

        if closest_node is not None:
            parent_node = insert_node_into_node(closest_node, parent_node, node)
            replace_node(ast, parent_node.id, parent_node)
    with open("ast.json", "w") as f:
        f.write(json.dumps(ast.dict(), indent=2))
    return ast
