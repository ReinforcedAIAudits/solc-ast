import json
import random
from typing import List, Union
from solc_ast_parser.models import ast_models
from solc_ast_parser.models.ast_models import (
    ElementaryTypeName,
    FunctionCall,
    IdentifierPath,
    ParameterList,
    SourceUnit,
    StructDefinition,
    TypeName,
    VariableDeclaration,
)
from solc_ast_parser.models.base_ast_models import NodeType
from solc_ast_parser.utils import find_node_with_properties, traverse_ast


def create_storage_declaration(
    storage_name: str,
    storage_type: TypeName,
    visibility: str = "internal",
    constant: bool = False,
    mutability: str = "nonpayable",
    state_variable: bool = False,
    storage_location: str = "",
) -> VariableDeclaration:
    return VariableDeclaration(
        name=storage_name,
        typeName=storage_type,
        constant=constant,
        mutability=mutability,
        stateVariable=state_variable,
        storageLocation=storage_location,
        visibility=visibility,
        nameLocation="",
        nodeType=NodeType.VARIABLE_DECLARATION,
        id=random.randint(0, 100000),
        src="",
    )


def create_elementary_type(type_name: str) -> ElementaryTypeName:
    return ElementaryTypeName(
        name=type_name if type_name is not None else "uint256",
        nodeType=NodeType.ELEMENTARY_TYPE_NAME,
        id=random.randint(0, 100000),
        src="",
    )


def create_struct_declaration(
    struct_name: str,
    struct_members: List[VariableDeclaration],
    visibility: str = "internal",
) -> StructDefinition:
    return StructDefinition(
        name=struct_name,
        nameLocation=" ",
        members=struct_members,
        visibility=visibility,
        nodeType=NodeType.STRUCT_DEFINITION,
        id=random.randint(0, 100000),
        src="",
    )


def create_event_definition(
    event_name: str,
    parameters: List[VariableDeclaration],
) -> ast_models.EventDefinition:
    return ast_models.EventDefinition(
        name=event_name,
        nameLocation="",
        parameters=ast_models.ParameterList(
            parameters=parameters,
            nodeType=NodeType.PARAMETER_LIST,
            id=random.randint(0, 100000),
            src="",
        ),
        anonymous=False,
        nodeType=NodeType.EVENT_DEFINITION,
        id=random.randint(0, 100000),
        src="",
    )


def create_array_type_name(base_type: ElementaryTypeName) -> ast_models.ArrayTypeName:
    return ast_models.ArrayTypeName(
        baseType=base_type,
        length=None,
        nodeType=NodeType.ARRAY_TYPE_NAME,
        id=random.randint(0, 100000),
        src="",
    )


def create_user_defined_type_name(type_name: str) -> ast_models.UserDefinedTypeName:
    return ast_models.UserDefinedTypeName(
        name=type_name,
        nodeType=NodeType.USER_DEFINED_TYPE_NAME,
        id=random.randint(0, 100000),
        src="",
    )


def append_declaration_to_contract(
    ast: SourceUnit, declaration: Union[VariableDeclaration, StructDefinition]
) -> SourceUnit:
    for ast_node in ast.nodes:
        if ast_node.node_type == NodeType.CONTRACT_DEFINITION:
            if declaration.node_type == NodeType.STRUCT_DEFINITION:
                ast_node.nodes.insert(0, declaration)
            else:
                last_struct_definition = next(
                    (
                        idx
                        for idx, contract_node in enumerate(reversed(ast_node.nodes))
                        if contract_node.node_type == NodeType.STRUCT_DEFINITION
                    ),
                    None,
                )
                if last_struct_definition:
                    ast_node.nodes.insert(last_struct_definition, declaration)
                else:
                    ast_node.nodes.insert(0, declaration)
            return ast
    raise ValueError("Contract not found in AST")


def restore_storages(ast: SourceUnit) -> SourceUnit:
    storages = [
        s.name
        for s in find_node_with_properties(ast, node_type=NodeType.VARIABLE_DECLARATION)
    ]

    function_calls = [
        f.expression
        for f in find_node_with_properties(ast, node_type=NodeType.FUNCTION_CALL)
    ]
    builtin_storages = ["msg", "block", "tx", "now", "gasleft", "this"]
    storage_types = {}
    events_to_create = {}

    def analyze_storage_type(node: ast_models.ASTNode):
        if node.node_type == NodeType.INDEX_ACCESS:
            base_name = extract_expression_name(node.base_expression)
            if (
                base_name not in storages
                and base_name not in storage_types
                and node not in function_calls
            ):
                storage_types[base_name] = "array"
        elif node.node_type == NodeType.MEMBER_ACCESS:
            if node.expression.node_type == NodeType.INDEX_ACCESS:
                base_name = extract_expression_name(node.expression)
                if (
                    base_name not in storages
                    and base_name not in storage_types
                    and node not in function_calls
                ):
                    storage_types[base_name] = "struct array"
            else:
                base_name = extract_expression_name(node.expression)
                if (
                    base_name not in storages
                    and base_name not in storage_types
                    and node not in function_calls
                ):
                    storage_types[base_name] = "struct"

        elif node.node_type == NodeType.EMIT_STATEMENT:
            if hasattr(node.event_call, "expression"):
                event_name = extract_expression_name(node.event_call.expression)
                if not event_name in list(events_to_create.keys()):
                    events_to_create[event_name] = node.event_call.arguments
        elif node.node_type == NodeType.FUNCTION_CALL:
            if hasattr(node, "expression") and hasattr(node.expression, "member_name"):
                if node.expression.member_name in [
                    "transfer",
                    "send",
                    "call",
                    "sender",
                ]:
                    base_name = extract_expression_name(node.expression.expression)
                    if base_name not in storages:
                        storage_types[base_name] = "address"
        elif node.node_type == NodeType.IDENTIFIER:
            if (
                node.name not in storages
                and node.name not in storage_types
                and node not in function_calls
            ):
                storage_types[node.name] = "uint256"

    traverse_ast(ast, analyze_storage_type)

    for event_name, event_args in events_to_create.items():
        event_params = []
        for arg in event_args:
            param_type = "address" if is_likely_address(arg, ast) else "uint256"
            event_params.append(
                create_storage_declaration(
                    storage_name=f"param{len(event_params)}",
                    storage_type=create_elementary_type(param_type),
                )
            )

        event_declaration = create_event_definition(
            event_name=event_name, parameters=event_params
        )
        ast = append_declaration_to_contract(ast, event_declaration)

    for storage_name, storage_type in storage_types.items():
        storages = [
            s.name
            for s in find_node_with_properties(
                ast, node_type=NodeType.VARIABLE_DECLARATION
            )
        ]

        if (
            storage_type == "array"
            and storage_name not in storages
            and storage_name not in builtin_storages
        ):
            storage_declaration = create_storage_declaration(
                storage_name=storage_name,
                storage_type=ast_models.ArrayTypeName(
                    baseType=create_elementary_type("uint256"),
                    length=None,
                    nodeType=NodeType.ARRAY_TYPE_NAME,
                    id=random.randint(0, 100000),
                    src="",
                ),
            )
        elif (
            storage_type == "struct"
            and storage_name not in storages
            and storage_name not in builtin_storages
        ):
            struct_name = storage_name.capitalize()
            members = filter(
                lambda n: n.node_type == NodeType.MEMBER_ACCESS
                and extract_expression_name(n.expression) == storage_name,
                find_node_with_properties(ast, node_type=NodeType.MEMBER_ACCESS),
            )
            struct_decl = create_struct_declaration(
                struct_name=struct_name,
                struct_members=[
                    create_storage_declaration(
                        storage_name=member.member_name,
                        storage_type=create_elementary_type("uint256"),
                    )
                    for member in members
                ],
            )
            ast = append_declaration_to_contract(ast, struct_decl)

            storage_declaration = create_storage_declaration(
                storage_name=storage_name,
                storage_type=ast_models.UserDefinedTypeName(
                    nodeType=NodeType.USER_DEFINED_TYPE_NAME,
                    id=random.randint(0, 100000),
                    src="",
                    pathNode=IdentifierPath(
                        nodeType=NodeType.IDENTIFIER_PATH,
                        id=random.randint(0, 100000),
                        src="",
                        nameLocations=[],
                        name=struct_name,
                    ),
                ),
            )
        elif (
            storage_type == "struct array"
            and storage_name not in storages
            and storage_name not in builtin_storages
        ):
            struct_name = storage_name.capitalize()
            members = filter(
                lambda n: n.node_type == NodeType.MEMBER_ACCESS
                and extract_expression_name(n.expression) == storage_name,
                find_node_with_properties(ast, node_type=NodeType.MEMBER_ACCESS),
            )
            struct_decl = create_struct_declaration(
                struct_name=struct_name,
                struct_members=[
                    create_storage_declaration(
                        storage_name=member.member_name,
                        storage_type=create_elementary_type("uint256"),
                    )
                    for member in members
                ],
            )
            ast = append_declaration_to_contract(ast, struct_decl)

            storage_declaration = create_storage_declaration(
                storage_name=storage_name,
                storage_type=ast_models.ArrayTypeName(
                    baseType=ast_models.UserDefinedTypeName(
                        nodeType=NodeType.USER_DEFINED_TYPE_NAME,
                        id=random.randint(0, 100000),
                        src="",
                        pathNode=IdentifierPath(
                            nodeType=NodeType.IDENTIFIER_PATH,
                            id=random.randint(0, 100000),
                            src="",
                            nameLocations=[],
                            name=struct_name,
                        ),
                    ),
                    length=None,
                    nodeType=NodeType.ARRAY_TYPE_NAME,
                    id=random.randint(0, 100000),
                    src="",
                ),
            )

        elif (
            storage_type == "address"
            and storage_name not in storages
            and storage_name not in builtin_storages
        ):
            storage_declaration = create_storage_declaration(
                storage_name=storage_name,
                storage_type=create_elementary_type("address"),
            )
        elif storage_name not in storages and storage_name not in builtin_storages:

            storage_declaration = create_storage_declaration(
                storage_name=storage_name,
                storage_type=create_elementary_type("uint256"),
            )
        else:
            continue

        ast = append_declaration_to_contract(ast, storage_declaration)

    return ast


def is_likely_address(node: ast_models.ASTNode, ast: SourceUnit) -> bool:
    if node.node_type == NodeType.IDENTIFIER:
        for parent in find_parent_nodes(ast, node):
            if parent.node_type == NodeType.FUNCTION_CALL:
                if hasattr(parent.expression, "member_name"):
                    if parent.expression.member_name in [
                        "transfer",
                        "send",
                        "call",
                        "sender",
                    ]:
                        return True
    return False


def find_parent_nodes(
    ast: SourceUnit, target_node: ast_models.ASTNode
) -> List[ast_models.ASTNode]:
    parents = []

    def collect_parents(node: ast_models.ASTNode):
        for field_name, field in node.model_fields.items():
            value = getattr(node, field_name)
            if isinstance(value, list):
                for item in value:
                    if item == target_node:
                        parents.append(node)
                    elif hasattr(item, "__fields__") and hasattr(item, "node_type"):
                        collect_parents(item)
            elif value == target_node:
                parents.append(node)
            elif hasattr(value, "__fields__") and hasattr(value, "node_type"):
                collect_parents(value)

    traverse_ast(ast, collect_parents)
    return parents


def extract_type_name(node: ast_models.TypeName) -> str:
    match node.node_type:
        case NodeType.ELEMENTARY_TYPE_NAME:
            return node.name
        case NodeType.MAPPING:
            return f"mapping({extract_type_name(node.key_type)} => {extract_type_name(node.value_type)})"
        case NodeType.ARRAY_TYPE_NAME:
            return f"{extract_type_name(node.base_type)}[]"
        case NodeType.FUNCTION_TYPE_NAME:
            return f"function({', '.join([extract_type_name(param) for param in node.parameter_types])}){extract_type_name(node.return_parameter_types)}"
        case NodeType.USER_DEFINED_TYPE_NAME:
            return node.path_node.name
    return None


def extract_expression_type(
    ast: ast_models.ASTNode, node: ast_models.Expression
) -> str:
    type_name = []

    match node.node_type:
        case NodeType.IDENTIFIER:
            traverse_ast(
                ast,
                lambda n: (
                    type_name.append(extract_type_name(n.type_name))
                    if n.node_type == NodeType.VARIABLE_DECLARATION
                    and n.name == node.name
                    else None
                ),
            )
        case NodeType.FUNCTION_CALL:
            traverse_ast(
                ast,
                lambda n: (
                    type_name.extend(
                        [
                            extract_type_name(param.type_name)
                            for param in n.return_parameters
                        ]
                    )
                    if n.node_type == NodeType.FUNCTION_DEFINITION
                    and n.name == extract_expression_name(node.expression)
                    else None
                ),
            )
        case NodeType.INDEX_ACCESS:
            traverse_ast(
                ast,
                lambda n: (
                    type_name.append(extract_type_name(n.type_name))
                    if n.node_type == NodeType.VARIABLE_DECLARATION
                    and n.name == node.base_expression.name
                    else None
                ),
            )
        case NodeType.INDEX_RANGE_ACCESS:
            traverse_ast(
                ast,
                lambda n: (
                    type_name.append(extract_type_name(n.type_name))
                    if n.node_type == NodeType.VARIABLE_DECLARATION
                    and n.name == node.base_expression.name
                    else None
                ),
            )
        case NodeType.MEMBER_ACCESS:
            traverse_ast(
                ast,
                lambda n: (
                    type_name.append(extract_type_name(n.type_name))
                    if n.node_type == NodeType.VARIABLE_DECLARATION
                    and n.name == node.expression.name
                    else None
                ),
            )
        case NodeType.BINARY_OPERATION:
            type_name.append(extract_expression_type(ast, node.left_expression))
        case NodeType.UNARY_OPERATION:
            type_name.append(extract_expression_type(ast, node.sub_expression))
        case NodeType.LITERAL:
            type_name.append(node.kind)
        case NodeType.TUPLE_EXPRESSION:
            type_name.extend(
                [
                    extract_expression_type(ast, expression)
                    for expression in node.components
                ]
            )
        case _:
            raise ValueError(f"Unsupported node type: {node.node_type}")
    return type_name[0] if type_name else None


def extract_expression_name(node: ast_models.Expression) -> str:
    match node.node_type:
        case NodeType.IDENTIFIER:
            return node.name
        case NodeType.FUNCTION_CALL:
            return extract_expression_name(node.expression)
        case NodeType.INDEX_ACCESS:
            return extract_expression_name(node.base_expression)
        case NodeType.MEMBER_ACCESS:
            return extract_expression_name(node.expression)
        case NodeType.BINARY_OPERATION:
            return extract_expression_name(node.left_expression)
        case NodeType.UNARY_OPERATION:
            return extract_expression_name(node.sub_expression)
        case NodeType.TUPLE_EXPRESSION:
            return [
                extract_expression_name(expression) for expression in node.components
            ]
        case NodeType.ELEMENTARY_TYPE_NAME_EXPRESSION:
            return node.type_name.name
        case NodeType.LITERAL:
            return node.value
        case _:
            print(json.dumps(node.model_dump(), indent=4))
            raise ValueError(f"Unsupported node type: {node.node_type}")


def restore_function_definitions(ast: SourceUnit) -> List[ast_models.ASTNode]:
    def restore_function_arguments(node: FunctionCall):
        args = []
        for argument in node.arguments:
            type_name = extract_expression_type(ast, argument)
            if type_name:
                args.append(
                    create_storage_declaration(
                        storage_name=extract_expression_name(argument),
                        storage_type=create_elementary_type(type_name),
                    )
                )
        return args

    function_calls = find_node_with_properties(ast, node_type=NodeType.FUNCTION_CALL)
    event_defintions = [
        e.name
        for e in find_node_with_properties(ast, node_type=NodeType.EVENT_DEFINITION)
    ]
    function_definitions = find_node_with_properties(
        ast, node_type=NodeType.FUNCTION_DEFINITION
    )
    storages = [
        s.name
        for s in find_node_with_properties(ast, node_type=NodeType.VARIABLE_DECLARATION)
    ]

    builtin_functions = [
        "require",
        "revert",
        "assert",
        "address",
        "uint256",
        "int256",
        "bool",
        "string",
        "bytes",
    ]
    restored_functions = []
    for function_call in function_calls:
        function_names = [f.name for f in function_definitions]
        function_name = extract_expression_name(function_call.expression)
        if (
            function_name not in function_names
            and function_name not in builtin_functions
            and function_name not in storages
            and function_name not in event_defintions
        ):
            function_arguments = restore_function_arguments(function_call)
            restored_functions.append(
                ast_models.FunctionDefinition(
                    name=function_name,
                    nameLocation="",
                    parameters=ParameterList(
                        parameters=function_arguments,
                        nodeType=NodeType.PARAMETER_LIST,
                        id=random.randint(0, 100000),
                        src="",
                    ),
                    returnParameters=ParameterList(
                        parameters=[],
                        nodeType=NodeType.PARAMETER_LIST,
                        id=random.randint(0, 100000),
                        src="",
                    ),
                    implemented=True,
                    visibility="internal",
                    stateMutability="nonpayable",
                    nodeType=NodeType.FUNCTION_DEFINITION,
                    id=random.randint(0, 100000),
                    src="",
                    kind="function",
                )
            )
    return restored_functions


def restore_ast(ast: SourceUnit) -> SourceUnit:
    ast = restore_storages(ast)

    function_declarations = restore_function_definitions(ast)
    for decl in function_declarations:
        for node in ast.nodes:
            if node.node_type == NodeType.CONTRACT_DEFINITION:
                node.nodes.append(decl)

    return ast
