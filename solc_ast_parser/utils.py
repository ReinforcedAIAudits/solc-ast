from collections import deque
import json
import random
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, get_args, get_origin
import solcx

from solc_ast_parser.models import ast_models
from solc_ast_parser.models.ast_models import SourceUnit
from solc_ast_parser.models.base_ast_models import Comment, MultilineComment, NodeType


# def traverse_ast(
#     node: ast_models.ASTNode,
#     visitor: Callable[[Any], None],
#     parent: Optional[ast_models.ASTNode] = None,
# ):
#     if node is None:
#         return

#     visitor(node, parent)

#     fields = node.model_fields

#     for field_name, field in fields.items():
#         value = getattr(node, field_name)

#         if isinstance(value, list):
#             for item in value:
#                 if hasattr(item, "__fields__") and hasattr(item, "node_type"):
#                     traverse_ast(item, visitor, node)

#         elif hasattr(value, "__fields__") and hasattr(value, "node_type"):
#             traverse_ast(value, visitor, node)


# def replace_node(
#     node: ast_models.ASTNode,
#     visitor: Callable[[Any, Optional[ast_models.ASTNode]], Any],
#     parent: Optional[ast_models.ASTNode] = None,
# ) -> ast_models.ASTNode:
#     if node is None:
#         return None

#     new_node = visitor(node, parent)

#     current_node = new_node if new_node is not None else node

#     fields = current_node.model_fields

#     for field_name, field in fields.items():
#         value = getattr(current_node, field_name)

#         if isinstance(value, list):
#             new_list = []
#             for item in value:
#                 if hasattr(item, "__fields__") and hasattr(item, "node_type"):
#                     new_item = replace_node(item, visitor, current_node)
#                     new_list.append(new_item if new_item is not None else item)
#                 else:
#                     new_list.append(item)
#             setattr(current_node, field_name, new_list)

#         elif hasattr(value, "__fields__") and hasattr(value, "node_type"):
#             new_value = replace_node(value, visitor, current_node)
#             if new_value is not None:
#                 setattr(current_node, field_name, new_value)

#     return current_node

# def create_standart_solidity_input(contract_content: str, contract_name: str) -> dict:
#     return {
#         "language": "Solidity",
#         "sources": {
#             contract_name: {
#                 "content": contract_content,
#             },
#         },
#         "settings": {
#             "stopAfter": "parsing",
#             "outputSelection": {"*": {"": ["ast"]}},
#         },
#     }


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


# def insert_comments_into_ast(source_code: str, ast: SourceUnit) -> SourceUnit:
#     single_line_comments = find_single_line_comments(source_code)
#     multiline_comments = find_multiline_comments(source_code)

#     comment_nodes = []

#     for start, text in single_line_comments:
#         comment_nodes.append(
#             Comment(
#                 src=f"{start}:{len(text)}:0",
#                 text=text.strip("/ "),
#                 id=random.randint(0, 1000000),
#                 nodeType=NodeType.COMMENT,
#             )
#         )

#     for start, text in multiline_comments:
#         comment_nodes.append(
#             MultilineComment(
#                 src=f"{start}:{len(text)}:0",
#                 text=text,
#                 id=random.randint(0, 1000000),
#                 nodeType=NodeType.MULTILINE_COMMENT,
#             )
#         )

#     comment_nodes.sort(key=lambda x: int(x.src.split(":")[0]))

#     return insert_nodes_into_ast(ast, comment_nodes)


# def find_single_line_comments(source: str) -> List[Tuple[int, str]]:
#     comments = []
#     pattern = r"//.*?(?=\n|$)"

#     for match in re.finditer(pattern, source):
#         start = match.start()
#         text = match.group()
#         comments.append((start, text))

#     return comments


# def find_multiline_comments(source: str) -> List[Tuple[int, str]]:
#     comments = []
#     pattern = r"/\*.*?\*/"

#     for match in re.finditer(pattern, source, re.DOTALL):
#         start = match.start()
#         text = match.group()
#         comments.append((start, text))

#     return comments


# def insert_node_into_node(
#     node: ast_models.ASTNode,
#     parent_node: ast_models.ASTNode,
#     new_node: ast_models.ASTNode,
# ):
#     if node == new_node or is_descendant(node, new_node):
#         return parent_node

#     match parent_node.node_type:
#         case NodeType.SOURCE_UNIT:
#             parent_node.nodes.insert(parent_node.nodes.index(node), new_node)
#         case NodeType.CONTRACT_DEFINITION:
#             parent_node.statements.insert(parent_node.statements.index(node), new_node)
#         case NodeType.BLOCK:
#             parent_node.statements.insert(parent_node.statements.index(node), new_node)
#         case _:
#             parent_node.comment = new_node

#     return parent_node


# # def is_descendant(node: ast_models.ASTNode, potential_descendant: ast_models.ASTNode) -> bool:
# #     # Implement logic to check if potential_descendant is a descendant of node
# #     # This will depend on your AST structure
# #     current = potential_descendant
# #     while current:
# #         if current == node:
# #             return True
# #         current = current.parent  # Assuming you have a parent attribute
# #     return False


# def insert_nodes_into_ast(ast: SourceUnit, nodes: List[Comment]) -> SourceUnit:
#     for node in nodes:
#         min_distance = 1000000
#         closest_node: ast_models.ASTNode = None
#         parent_node: ast_models.ASTNode = None

#         def is_closest_node(
#             node: ast_models.ASTNode, parent: Optional[ast_models.ASTNode]
#         ):
#             nonlocal min_distance, closest_node, parent_node
#             start = int(node.src.split(":")[0])
#             if abs(start - int(node.src.split(":")[1])) < min_distance:
#                 min_distance = abs(start - int(node.src.split(":")[1]))
#                 closest_node = node
#                 parent_node = parent

#         traverse_ast(ast, is_closest_node)
#         if closest_node is not None:
#             ast = replace_node(
#                 ast,
#                 lambda x, parent: insert_node_into_node(x, parent, node)
#                 if x == closest_node
#                 else x,
#             )

#     return ast
import json
import random
import re
from typing import Any, Callable, Dict, List, Optional, Tuple
import solcx

from solc_ast_parser.models import ast_models
from solc_ast_parser.models.ast_models import SourceUnit
from solc_ast_parser.models.base_ast_models import Comment, MultilineComment, NodeType


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


# def replace_node(
#     node: ast_models.ASTNode,
#     visitor: Callable[[Any, Optional[ast_models.ASTNode]], Any],
#     parent: Optional[ast_models.ASTNode] = None,
#     visited: Optional[set] = None,
# ) -> ast_models.ASTNode:
#     if node is None:
#         return None
        
#     if visited is None:
#         visited = set()
        
#     if node.id in visited:
#         return node
        
    
#     visited.add(node.id)

#     new_node = visitor(node, parent)
#     current_node = new_node if new_node is not None else node

#     for field_name, field in current_node.model_fields.items():
#         value = getattr(current_node, field_name)

#         if isinstance(value, list):
#             new_list = []
#             for item in value:
#                 if hasattr(item, "__fields__") and hasattr(item, "node_type"):
#                     new_item = replace_node(item, visitor, current_node, visited)
#                     new_list.append(new_item if new_item is not None else item)
#                 else:
#                     new_list.append(item)
#             setattr(current_node, field_name, new_list)
#         elif hasattr(value, "__fields__") and hasattr(value, "node_type"):
#             new_value = replace_node(value, visitor, current_node, visited)
#             if new_value is not None:
#                 setattr(current_node, field_name, new_value)

#     return current_node


def replace_node(ast_node: Any, target_id: int, replacement_node: Any) -> bool:
    """
    Iteratively replaces a node with given id in the AST tree with a replacement node.
    
    Args:
        ast_node: Root node of AST
        target_id: ID of the node to replace
        replacement_node: New node to put in place of the target
        
    Returns:
        bool: True if replacement was successful, False otherwise
    """
    if hasattr(ast_node, 'id') and ast_node.id == target_id:
        return False  # Can't replace root node
    
    # Stack contains tuples of (parent_node, field_name, index_if_list)
    stack = deque([(ast_node, None, None)])
    
    while stack:
        current_node, parent_field, list_index = stack.popleft()
        
        for field_name, field_value in current_node.__dict__.items():
            # Handle lists
            if isinstance(field_value, list):
                for i, item in enumerate(field_value):
                    if hasattr(item, 'id') and item.id == target_id:
                        field_value[i] = replacement_node
                        return True
                    elif hasattr(item, '__dict__'):
                        stack.append((item, field_name, i))
                        
            # Handle nested objects
            elif hasattr(field_value, '__dict__'):
                if hasattr(field_value, 'id') and field_value.id == target_id:
                    setattr(current_node, field_name, replacement_node)
                    return True
                stack.append((field_value, field_name, None))
                
    return False


def create_standard_solidity_input(contract_content: str, contract_name: str) -> Dict:
    """Create standardized Solidity compiler input."""
    return {
        "language": "Solidity",
        "sources": {contract_name: {"content": contract_content}},
        "settings": {
            "stopAfter": "parsing",
            "outputSelection": {"*": {"": ["ast"]}},
        },
    }


def find_comments(source: str) -> List[Tuple[int, str, bool]]:
    """Find both single-line and multiline comments in source code."""
    comments = []

    # Single line comments
    for match in re.finditer(r"//.*?(?=\n|$)", source):
        comments.append((match.start(), match.group().strip("/ "), False))

    # Multiline comments
    for match in re.finditer(r"/\*.*?\*/", source, re.DOTALL):
        comments.append((match.start(), match.group(), True))

    return sorted(comments, key=lambda x: x[0])


def create_comment_node(start: int, text: str, is_multiline: bool) -> Comment:
    """Create a comment node with given parameters."""
    node_class = MultilineComment if is_multiline else Comment
    return node_class(
        src=f"{start}:{len(text)}:0",
        text=text,
        id=random.randint(0, 1000000),
        nodeType=NodeType.MULTILINE_COMMENT if is_multiline else NodeType.COMMENT,
    )


def insert_comments_into_ast(source_code: str, ast: SourceUnit) -> SourceUnit:
    """Insert comments into AST."""
    comments = find_comments(source_code)
    comment_nodes = [
        create_comment_node(start, text, is_multiline)
        for start, text, is_multiline in comments
    ]
    return insert_nodes_into_ast(ast, comment_nodes)


def insert_node_into_node(
    node: ast_models.ASTNode,
    parent_node: ast_models.ASTNode,
    new_node: ast_models.ASTNode,
) -> ast_models.ASTNode:
    """Insert a new node into the parent node."""
    if node == new_node:
        return parent_node
    
    if not parent_node:
        return node
    
    with open("node.txt", "a") as f:
        f.write(str(node))
    # print(node)

    if parent_node.node_type in (NodeType.SOURCE_UNIT, NodeType.CONTRACT_DEFINITION):
        parent_node.nodes.insert(parent_node.nodes.index(node), new_node)
    elif parent_node.node_type == NodeType.BLOCK:
        parent_node.statements.insert(parent_node.statements.index(node), new_node)
    else:
        parent_node.comment = new_node

    with open("parent_node.txt", "a") as f:
        f.write(str(parent_node))
    return parent_node


def insert_nodes_into_ast(ast: SourceUnit, nodes: List[Comment]) -> SourceUnit:
    """Insert multiple nodes into AST."""
    for node in nodes:
        print(node)
        min_distance = float("inf")
        closest_node = None
        parent_node = None

        def find_closest_node(
            current_node: ast_models.ASTNode, parent: Optional[ast_models.ASTNode]
        ) -> None:
            nonlocal min_distance, closest_node, parent_node
            start = int(current_node.src.split(":")[0])
            distance = start - int(node.src.split(":")[0])
            if  0 < distance < min_distance:
                min_distance = distance
                closest_node = current_node
                parent_node = parent

        traverse_ast(ast, find_closest_node)

        if closest_node is not None:
            # ast = replace_node(
            #     ast,
            #     lambda x, parent: (
            #         insert_node_into_node(x, parent, node) if x == closest_node else x
            #     ),
            # )
            # replace_node(ast, closest_node.id, node)
            parent_node = insert_node_into_node(closest_node, parent_node, node)
            replace_node(ast, parent_node.id, parent_node)

    return ast
