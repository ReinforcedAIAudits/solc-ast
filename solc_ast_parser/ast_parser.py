from typing import Union

from solc_ast_parser.models import yul_models
from .models.ast_models import (
    ArrayTypeName,
    Assignment,
    Block,
    Break,
    Conditional,
    Continue,
    ContractDefinition,
    ElementaryTypeNameExpression,
    EmitStatement,
    EnumDefinition,
    EnumValue,
    ErrorDefinition,
    ExpressionStatement,
    ForStatement,
    FunctionCallOptions,
    FunctionNode,
    FunctionTypeName,
    IdentifierPath,
    IfStatement,
    ImportDirective,
    IndexRangeAccess,
    InheritanceSpecifier,
    Literal,
    Mapping,
    BinaryOperation,
    ElementaryTypeName,
    EventDefinition,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    IndexAccess,
    MemberAccess,
    ModifierDefinition,
    ModifierInvocation,
    NewExpression,
    OverrideSpecifier,
    ParameterList,
    PlaceholderStatement,
    PragmaDirective,
    Return,
    RevertStatement,
    SourceUnit,
    StructDefinition,
    StructuredDocumentation,
    Throw,
    TryCatchClause,
    TryStatement,
    TupleExpression,
    UnaryOperation,
    UserDefinedTypeName,
    UserDefinedValueTypeDefinition,
    UsingForDirective,
    VariableDeclaration,
    VariableDeclarationStatement,
    WhileStatement,
)
from .models import ast_models
from .models.base_ast_models import NodeType, YulNodeType


def parse_yul_literal(node: yul_models.YulLiteral, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{node.value}"


def parse_yul_identifier(node: yul_models.YulIdentifier, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{node.name}"


def parse_yul_builtin_name(
    node: yul_models.YulBuiltinName, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}{node.name}"


def parse_yul_assignment(node: yul_models.YulAssignment, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{', '.join([parse_yul_node(var) for var in node.variable_names])} := {parse_yul_node(node.value)}"


def parse_yul_function_call(
    node: yul_models.YulFunctionCall, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}{parse_yul_node(node.function_name, spaces_count)}({', '.join([parse_yul_node(arg) for arg in node.arguments])})"


def parse_yul_expression_statement(
    node: yul_models.YulExpressionStatement, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}{parse_yul_node(node.expression, spaces_count)}"


def parse_yul_variable_declaration(
    node: yul_models.YulVariableDeclaration, spaces_count: int = 0
) -> str:
    value = f" := {parse_yul_node(node.value, spaces_count)}" if node.value else ""
    variables = ",".join([parse_yul_node(var, spaces_count) for var in node.variables])
    return f"{' ' * spaces_count}{variables}{value}"


def parse_yul_function_definition(
    node: yul_models.YulFunctionDefinition, spaces_count: int = 0
) -> str:
    parameters = ", ".join([parse_yul_node(param) for param in node.parameters])
    return_variables = ", ".join(
        [parse_yul_node(return_variable) for return_variable in node.return_variables]
    )
    return f"{' ' * spaces_count}function {node.name}({parameters}) -> {return_variables} {parse_yul_node(node.body)}"


def parse_yul_if(node: yul_models.YulIf, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}if {parse_yul_node(node.condition)} {parse_yul_block(node.body, spaces_count, True)}"


def parse_yul_case(node: yul_models.YulCase, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}case {node.value} {parse_yul_block(node.body, spaces_count=0, new_line=True)}"


def parse_yul_switch(node: yul_models.YulSwitch, spaces_count: int = 0) -> str:
    cases = "\n".join([parse_yul_node(case, spaces_count) for case in node.cases])
    return f"{' ' * spaces_count}switch {parse_yul_node(node.expression)} {cases}"


def parse_yul_for_loop(node: yul_models.YulForLoop, spaces_count: int = 0) -> str:
    pre_arr = []
    for statement in node.pre.statements:
        if statement.node_type == YulNodeType.YUL_VARIABLE_DECLARATION:
            pre_arr.append(f"let {parse_yul_node(statement)}")
        else:
            pre_arr.append(parse_yul_node(statement))
    return f"{' ' * spaces_count}for {{ {', '.join(pre_arr)} }} {parse_yul_node(node.condition)} {parse_yul_node(node.post)} {parse_yul_block(node.body, spaces_count, True)}"


def parse_yul_break(node: yul_models.YulBreak, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}break"


def parse_yul_continue(node: yul_models.YulContinue, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}continue"


def parse_yul_leave(node: yul_models.YulLeave, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}leave"


def parse_yul_typed_name(node: yul_models.YulTypedName, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{node.name}"


def parse_yul_block(
    node: yul_models.YulBlock, spaces_count: int = 0, new_line: bool = False
) -> str:
    if len(node.statements) == 1 and not new_line:
        return f"{{ {parse_yul_node(node.statements[0])} }}\n"

    if not node.statements:
        return "{ }\n"

    statements = "\n".join(
        [parse_yul_node(statement, spaces_count + 4) for statement in node.statements]
    )
    return f"{{\n{statements}\n{' ' * spaces_count}}}\n"


def parse_yul_node(node: yul_models.YulNode, spaces_count: int = 0):
    match node.node_type:
        case YulNodeType.YUL_BLOCK:
            return parse_yul_block(node, spaces_count)
        case YulNodeType.YUL_LITERAL:
            return parse_yul_literal(node, spaces_count)
        case YulNodeType.YUL_IDENTIFIER:
            return parse_yul_identifier(node, spaces_count)
        case YulNodeType.YUL_BUILTIN_NAME:
            return parse_yul_builtin_name(node, spaces_count)
        case YulNodeType.YUL_ASSIGNMENT:
            return parse_yul_assignment(node, spaces_count)
        case YulNodeType.YUL_FUNCTION_CALL:
            return parse_yul_function_call(node, spaces_count)
        case YulNodeType.YUL_EXPRESSION_STATEMENT:
            return parse_yul_expression_statement(node, spaces_count)
        case YulNodeType.YUL_VARIABLE_DECLARATION:
            return parse_yul_variable_declaration(node, spaces_count)
        case YulNodeType.YUL_FUNCTION_DEFINITION:
            return parse_yul_function_definition(node, spaces_count)
        case YulNodeType.YUL_IF:
            return parse_yul_if(node, spaces_count)
        case YulNodeType.YUL_CASE:
            return parse_yul_case(node, spaces_count)
        case YulNodeType.YUL_SWITCH:
            return parse_yul_switch(node, spaces_count)
        case YulNodeType.YUL_FOR_LOOP:
            return parse_yul_for_loop(node, spaces_count)
        case YulNodeType.YUL_BREAK:
            return parse_yul_break(node, spaces_count)
        case YulNodeType.YUL_CONTINUE:
            return parse_yul_continue(node, spaces_count)
        case YulNodeType.YUL_LEAVE:
            return parse_yul_leave(node, spaces_count)
        case YulNodeType.YUL_TYPED_NAME:
            return parse_yul_typed_name(node, spaces_count)
        case _:
            raise ValueError(f"Unknown node type: {node.node_type}")


def parse_literal(node: Literal, spaces_count: int = 0) -> str:
    subdenomination = f" {node.subdenomination}" if node.subdenomination else ""
    if node.kind == "string":
        return f"{' ' * spaces_count}{repr(node.value)}{subdenomination}"
    return f"{' ' * spaces_count}{node.value}{subdenomination}"


def parse_index_access(node: IndexAccess, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{parse_ast_node(node.base_expression)}[{parse_ast_node(node.index_expression) if node.index_expression else ''}]"


def parse_member_access(node: MemberAccess, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{parse_ast_node(node.expression)}.{node.member_name}"


def parse_parameter_list(node: ParameterList, spaces_count: int = 0) -> str:
    parsed = []
    for parameter in node.parameters:
        storage_location = (
            f" {parameter.storage_location}"
            if parameter.storage_location != "default"
            else ""
        )
        var_type = parse_ast_node(parameter.type_name)
        name = f" {parameter.name}" if parameter.name else ""
        if parameter.node_type == NodeType.VARIABLE_DECLARATION:
            indexed = " indexed" if parameter.indexed else ""
        parsed.append(f"{var_type}{indexed}{storage_location}{name}")
    return ", ".join(parsed)


def parse_unary_operation(node: UnaryOperation, spaces_count: int = 0) -> str:
    if node.prefix:
        return (
            f"{' ' * spaces_count}{node.operator}{parse_ast_node(node.sub_expression)}"
        )
    else:
        return (
            f"{' ' * spaces_count}{parse_ast_node(node.sub_expression)}{node.operator}"
        )


def parse_binary_operation(node: BinaryOperation, spaces_count: int = 0):
    return f"{' ' * spaces_count}{parse_ast_node(node.left_expression)} {node.operator} {parse_ast_node(node.right_expression)}"


def parse_function_call(node: FunctionCall, spaces_count: int = 0) -> str:
    arguments = [parse_ast_node(arg) for arg in node.arguments]
    if len(node.names) > 0:
        arguments = [f"{name}: {arg}" for name, arg in zip(node.names, arguments)]
        arguments_str = f"{{{', '.join(arguments)}}}"
    else:
        arguments_str = ', '.join(arguments)
    return f"{' ' * spaces_count}{parse_ast_node(node.expression)}({arguments_str})"


def parse_assignment(node: Assignment, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{parse_ast_node(node.left_hand_side)} {node.operator} {parse_ast_node(node.right_hand_side)}"


def parse_variable_declaration(node: VariableDeclaration, spaces_count: int = 0) -> str:
    storage_location = (
        f" {node.storage_location}" if node.storage_location != "default" else ""
    )
    visibility = f" {node.visibility}" if node.visibility != "internal" else ""
    value = ""
    if node.value:
        value = f" = {parse_ast_node(node.value)}"
    return f"{' ' * spaces_count}{parse_ast_node(node.type_name)}{visibility}{storage_location} {node.name}{value}"


def parse_tuple_expression(node: TupleExpression, spaces_count: int = 0) -> str:
    res_tuple = [parse_ast_node(component) for component in node.components]

    return f"{' ' * spaces_count}({', '.join(res_tuple)})"


def parse_variable_declaration_statement(
    node: VariableDeclarationStatement, spaces_count: int = 0
) -> str:

    declarations = []
    for declaration in node.declarations:
        if declaration is None:
            declarations.append("")
        else:
            declarations.append(parse_ast_node(declaration))
    if len(declarations) > 1:
        declarations_str = f"({', '.join(declarations)})"
    else:
        declarations_str = declarations[0]
    left = declarations_str
    right = f" = {parse_ast_node(node.initial_value)}" if node.initial_value else ""
    return f"{' ' * (spaces_count)}{left}{right}"


def parse_ast_node(node: ast_models.ASTNode, spaces_count: int = 0):
    match node.node_type:
        case NodeType.PRAGMA_DIRECTIVE:
            return parse_pragma_directive(node, spaces_count)
        # case NodeType.STRUCTURED_DOCUMENTATION:
        #     return  parse_structured_documentation(node, spaces_count)
        case NodeType.IDENTIFIER_PATH:
            return parse_identifier_path(node, spaces_count)
        case NodeType.INHERITANCE_SPECIFIER:
            return parse_inheritance_specifier(node, spaces_count)
        case NodeType.USING_FOR_DIRECTIVE:
            return parse_using_for_directive(node, spaces_count)
        case NodeType.PARAMETER_LIST:
            return parse_parameter_list(node, spaces_count)
        case NodeType.OVERRIDE_SPECIFIER:
            return parse_override_specifier(node, spaces_count)
        case NodeType.FUNCTION_DEFINITION:
            return parse_function_definition(node, spaces_count)
        case NodeType.MODIFIER_DEFINITION:
            return parse_modifier_definition(node, spaces_count)
        case NodeType.MODIFIER_INVOCATION:
            return parse_modifier_invocation(node, spaces_count)
        case NodeType.ERROR_DEFINITION:
            return parse_error_definition(node, spaces_count)
        case NodeType.EVENT_DEFINITION:
            return parse_event_definition(node, spaces_count)
        case NodeType.TRY_CATCH_CLAUSE:
            return parse_try_catch_clause(node, spaces_count)
        case NodeType.MAPPING:
            return parse_mapping(node, spaces_count)
        case NodeType.USER_DEFINED_TYPE_NAME:
            return parse_user_defined_type_name(node, spaces_count)
        case NodeType.FUNCTION_TYPE_NAME:
            return parse_function_type_name(node, spaces_count)
        case NodeType.ARRAY_TYPE_NAME:
            return parse_array_type_name(node, spaces_count)
        case NodeType.ELEMENTARY_TYPE_NAME:
            return parse_elementary_type_name(node, spaces_count)
        case NodeType.IDENTIFIER:
            return f"{' ' * spaces_count}{node.name}"
        case NodeType.LITERAL:
            return parse_literal(node, spaces_count)
        case NodeType.ELEMENTARY_TYPE_NAME_EXPRESSION:
            return parse_elementary_type_name_expression(node, spaces_count)
        case NodeType.CONDITIONAL:
            return parse_conditional(node, spaces_count)
        case NodeType.ASSIGNMENT:
            return parse_assignment(node, spaces_count)
        case NodeType.TUPLE_EXPRESSION:
            return parse_tuple_expression(node, spaces_count)
        case NodeType.UNARY_OPERATION:
            return parse_unary_operation(node, spaces_count)
        case NodeType.BINARY_OPERATION:
            return parse_binary_operation(node, spaces_count)
        case NodeType.FUNCTION_CALL:
            return parse_function_call(node, spaces_count)
        case NodeType.FUNCTION_CALL_OPTIONS:
            return parse_function_call_options(node, spaces_count)
        case NodeType.FUNCTION_NODE:
            return parse_function_node(node, spaces_count)
        case NodeType.INLINE_ASSEMBLY:
            return parse_inline_assembly(node, spaces_count)
        case NodeType.NEW_EXPRESSION:
            return parse_new_expression(node, spaces_count)
        case NodeType.MEMBER_ACCESS:
            return parse_member_access(node, spaces_count)
        case NodeType.INDEX_ACCESS:
            return parse_index_access(node, spaces_count)
        case NodeType.INDEX_RANGE_ACCESS:
            return parse_index_range_access(node, spaces_count)
        case NodeType.IMPORT_DIRECTIVE:
            return parse_import_directive(node, spaces_count)
        case NodeType.CONTRACT_DEFINITION:
            return parse_contract_definition(node, spaces_count)
        case NodeType.STRUCT_DEFINITION:
            return parse_struct_definition(node, spaces_count)
        case NodeType.ENUM_DEFINITION:
            return parse_enum_definition(node, spaces_count)
        case NodeType.ENUM_VALUE:
            return parse_enum_value(node, spaces_count)
        case NodeType.USER_DEFINED_VALUE_TYPE_DEFINITION:
            return parse_user_defined_value_type_definition(node, spaces_count)
        case NodeType.VARIABLE_DECLARATION:
            return parse_variable_declaration(node, spaces_count)
        case NodeType.BLOCK:
            return parse_block(node, spaces_count)
        case NodeType.PLACEHOLDER_STATEMENT:
            return parse_placeholder_statement(node, spaces_count)
        case NodeType.IF_STATEMENT:
            return parse_if_statement(node, spaces_count)
        case NodeType.TRY_STATEMENT:
            return parse_try_statement(node, spaces_count)
        case NodeType.FOR_STATEMENT:
            return parse_for_statement(node, spaces_count)
        case NodeType.CONTINUE:
            return parse_continue(node, spaces_count)
        case NodeType.BREAK:
            return parse_break(node, spaces_count)
        case NodeType.RETURN:
            return parse_return(node, spaces_count)
        case NodeType.THROW:
            return parse_throw(node, spaces_count)
        case NodeType.REVERT_STATEMENT:
            return parse_revert_statement(node, spaces_count)
        case NodeType.EMIT_STATEMENT:
            return parse_emit_statement(node, spaces_count)
        case NodeType.VARIABLE_DECLARATION_STATEMENT:
            return parse_variable_declaration_statement(node, spaces_count)
        case NodeType.EXPRESSION_STATEMENT:
            return parse_expression_statement(node, spaces_count)
        case NodeType.COMMENT:
            return f"{' ' * spaces_count}// {node.text}\n"
        case NodeType.MULTILINE_COMMENT:
            return f"{' ' * spaces_count}{node.text}\n"
        case _:
            raise ValueError(f"Unknown node type: {node.node_type}")


def parse_expression_statement(node: ExpressionStatement, spaces_count: int = 0) -> str:
    return f"{' ' * (spaces_count)}{parse_ast_node(node.expression)}"


def build_function_header(node: FunctionDefinition, spaces_count: int = 0) -> str:
    name = f" {node.name}" if node.name else ""
    visibility = f" {node.visibility}"
    mutability = (
        f" {node.state_mutability}" if node.state_mutability != "nonpayable" else ""
    )
    overrides = " override" if node.overrides else ""
    virtual = " virtual" if node.virtual else ""
    return_params = parse_ast_node(node.return_parameters)
    modifiers = (
        f" {', '.join([parse_ast_node(mod) for mod in node.modifiers])}"
        if node.modifiers
        else ""
    )

    if return_params:
        return_params = f" returns ({return_params})"

    if node.kind == "constructor":
        return f"{' ' * spaces_count}constructor({parse_ast_node(node.parameters)})"
    else:
        return f"{' ' * spaces_count}{node.kind}{name}({parse_ast_node(node.parameters)}){visibility}{virtual}{overrides}{modifiers}{mutability}{return_params}"


def parse_emit_statement(node: EmitStatement, spaces_count: int = 0) -> str:
    return f"{' ' * (spaces_count)}emit {parse_ast_node(node.event_call)};\n"


def parse_function_definition(node: FunctionDefinition, spaces_count: int = 0) -> str:
    result = ""

    result += build_function_header(node, spaces_count)
    if not node.body:
        return result + ";\n\n"
    body = parse_ast_node(node.body, spaces_count + 4)
    if body:
        result += f" {{\n{body}{' ' * spaces_count}}}\n\n"
    else:
        result += " {}\n\n"
    return result


def parse_mapping(node: Mapping, spaces_count: int = 0) -> str:
    key_type = parse_ast_node(node.key_type)
    value_type = parse_ast_node(node.value_type)
    return f"{' ' * spaces_count}mapping({key_type} => {value_type})"


def parse_user_defined_type_name(
    node: UserDefinedTypeName, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}{node.path_node.name}"


def parse_function_type_name(node: FunctionTypeName, spaces_count: int = 0) -> str:
    return f"{build_function_header(node)};\n"


def parse_array_type_name(node: ArrayTypeName, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{parse_ast_node(node.base_type)}[{node.length or ''}]"


def parse_elementary_type_name(node: ElementaryTypeName, spaces_count: int = 0) -> str:
    if node.name == "address" and node.state_mutability == "payable":
        return f"{' ' * spaces_count}{node.state_mutability}"
    return f"{' ' * spaces_count}{node.name}"


def parse_elementary_type_name_expression(
    node: ElementaryTypeNameExpression, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}{parse_ast_node(node.type_name)}"


def parse_conditional(node: Conditional, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{parse_ast_node(node.condition)} ? {parse_ast_node(node.true_expression)} : {parse_ast_node(node.false_expression)}"


def parse_function_call_options(
    node: FunctionCallOptions, spaces_count: int = 0
) -> str:
    options = [
        f"{name}: {parse_ast_node(option)}"
        for name, option in zip(node.names, node.options)
    ]
    return (
        f"{' ' * spaces_count}{parse_ast_node(node.expression)}{{{' ,'.join(options)}}}"
    )


def parse_new_expression(node: NewExpression, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}new {parse_ast_node(node.type_name)}"


def parse_import_directive(node: ImportDirective, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}import {node.absolute_path};"  # TODO needs to upgrade


def parse_index_range_access(node: IndexRangeAccess, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{parse_ast_node(node.base_expression)}[{parse_ast_node(node.start_expression)}:{parse_ast_node(node.end_expression)}]"


def parse_enum_value(node: EnumValue, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{node.name}"


def parse_user_defined_value_type_definition(
    node: UserDefinedValueTypeDefinition, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}struct {node.name} {{\n{' ' * spaces_count}}}\n"


def parse_placeholder_statement(
    node: PlaceholderStatement, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}_;\n"


def parse_continue(node: Continue, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}continue;\n"


def parse_break(node: Break, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}break;\n"


def parse_return(node: Return, spaces_count: int = 0) -> str:
    if node.expression:
        return f"{' ' * spaces_count}return {parse_ast_node(node.expression)}"
    else:
        return f"{' ' * spaces_count}return"


def parse_throw(node: Throw, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}throw;\n"


def parse_revert_statement(node: RevertStatement, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}revert({parse_ast_node(node.error_call)});\n"


def parse_for_statement(node: ForStatement, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}for ("
    if node.intialization_expression:
        result += f"{parse_ast_node(node.intialization_expression)}; "
    if node.condition:
        result += f"{parse_ast_node(node.condition)}; "
    if node.loop_expression:
        result += f"{parse_ast_node(node.loop_expression)}"
    result += f") {{\n"
    spaces_count += 4
    result += parse_ast_node(node.body, spaces_count)
    spaces_count -= 4
    result += f"{' ' * spaces_count}}}\n"
    return result


def parse_struct_definition(node: StructDefinition, spaces_count: int = 0) -> str:
    spaces = " " * spaces_count
    code = f"{' ' * spaces_count}struct {node.name} {{\n"
    spaces_count += 4
    for member in node.members:
        code += (
            f"{' ' * spaces_count}{parse_ast_node(member.type_name)} {member.name};\n"
        )
    spaces_count -= 4

    code += f"{' ' * spaces_count}}}\n"
    return code


def parse_event_definition(node: EventDefinition, spaces_count: int = 0) -> str:
    return (
        f"{' ' * spaces_count}event {node.name}({parse_ast_node(node.parameters)});\n"
    )


def parse_pragma_directive(node: PragmaDirective, spaces_count: int = 0) -> str:
    pragma_str = "".join(node.literals[1:])
    return f"{' ' * spaces_count}pragma {node.literals[0]} {pragma_str};\n\n"


def parse_contract_definition(node: ContractDefinition, spaces_count: int = 0) -> str:
    base_contracts = ""
    if len(node.base_contracts):
        base_contracts = [parse_ast_node(base) for base in node.base_contracts]
        base_contracts = f" is {', '.join(base_contracts)}"
    code = f"{node.contract_kind} {node.name}{base_contracts} {{{f' // {node.comment.text}' if node.comment else ''}\n"
    spaces_count = 4
    for contract_node in node.nodes:
        if contract_node.node_type == NodeType.VARIABLE_DECLARATION:
            code += f"{parse_variable_declaration(contract_node, spaces_count)};{f' // {contract_node.comment.text}' if contract_node.comment else ''}\n"
            continue
        code += parse_ast_node(contract_node, spaces_count)
    code += "}\n\n"

    return code


def parse_while_statement(node: WhileStatement, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}while ({parse_ast_node(node.condition)}) {{\n"
    spaces_count += 4
    result += parse_ast_node(node.body, spaces_count)
    spaces_count -= 4
    result += f"{' ' * spaces_count}}}\n"
    return result


def parse_if_statement(node: IfStatement, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}if ({parse_ast_node(node.condition)}) {{\n"
    spaces_count += 4
    result += parse_ast_node(node.true_body, spaces_count)
    spaces_count -= 4

    if node.false_body:
        result += f"{' ' * spaces_count}}} else {{\n"
        spaces_count += 4
        result += parse_ast_node(node.false_body, spaces_count)
        spaces_count -= 4

    result += f"{' ' * spaces_count}}}\n"
    return result


def parse_using_for_directive(node: UsingForDirective, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}using "

    if node.library_name:
        result += parse_ast_node(node.library_name)

    if node.function_list:
        funcs = [parse_ast_node(f) for f in node.function_list]
        result += f"{{{', '.join(funcs)}}}"

    result += " for "

    if node.type_name:
        result += parse_ast_node(node.type_name)
    else:
        result += "*"

    if node.global_:
        result += " global"

    return result + ";\n"


def parse_override_specifier(
    node: OverrideSpecifier, spaces_count: int = 0
) -> str:  ## TODO needs testing
    if node.overrides:
        overrides = [f.name for f in node.overrides]
    return f"{' ' * spaces_count}override({', '.join(overrides)}) "


def parse_modifier_definition(node: ModifierDefinition, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}modifier {node.name}({parse_ast_node(node.parameters)}) {{\n"
    spaces_count += 4
    result += parse_ast_node(node.body, spaces_count)
    spaces_count -= 4
    result += f"{' ' * spaces_count}}}\n"
    return result


def parse_modifier_invocation(node: ModifierInvocation, spaces_count: int = 0) -> str:
    arguments = (
        f"({', '.join([parse_ast_node(arg) for arg in node.arguments])})"
        if node.arguments
        else ""
    )
    return f"{' ' * spaces_count}{parse_ast_node(node.modifier_name)}{arguments}"


def parse_error_definition(node: ErrorDefinition, spaces_count: int = 0) -> str:
    return (
        f"{' ' * spaces_count}error {node.name}({parse_ast_node(node.parameters)});\n"
    )


def parse_function_node(node: FunctionNode, spaces_count: int = 0) -> str:
    if node.function:
        return parse_ast_node(node.function)
    elif node.operator:
        return node.operator
    return ""


def parse_inline_assembly(
    node: ast_models.InlineAssembly, spaces_count: int = 0
) -> str:
    return f"{' ' * spaces_count}assembly {parse_yul_node(node.AST, spaces_count)}"


def parse_identifier_path(node: IdentifierPath, spaces_count: int = 0) -> str:
    return f"{' ' * spaces_count}{node.name}"


def parse_inheritance_specifier(
    node: InheritanceSpecifier, spaces_count: int = 0
) -> str:
    result = parse_ast_node(node.base_name)
    if node.arguments:
        args = [parse_ast_node(arg) for arg in node.arguments]
        result += f"({', '.join(args)})"
    return result


def parse_enum_definition(node: EnumDefinition, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}enum {node.name} {{\n"
    spaces_count += 4
    members = [f"{' ' * spaces_count}{member.name}" for member in node.members]
    result += ",\n".join(members)
    spaces_count -= 4
    result += f"\n{' ' * spaces_count}}}\n"
    return result


def parse_try_catch_clause(node: TryCatchClause, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}catch "
    if node.parameters:
        result += f"({parse_ast_node(node.parameters)}) "
    result += "{\n"
    spaces_count += 4
    result += parse_ast_node(node.block, spaces_count)
    spaces_count -= 4
    result += f"{' ' * spaces_count}}}\n"
    return result


def parse_try_statement(node: TryStatement, spaces_count: int = 0) -> str:
    result = f"{' ' * spaces_count}try "
    if node.external_call:
        result += parse_ast_node(node.external_call)
    result += " {\n"

    for clause in node.clauses:
        result += parse_ast_node(clause, spaces_count)

    result += f"{' ' * spaces_count}}}\n"
    return result


def parse_block(node: Block, spaces_count: int = 0) -> str:
    result = ""
    for statement in node.statements:
        if not statement.node_type in (
            NodeType.COMMENT,
            NodeType.MULTILINE_COMMENT,
        ):
            result += parse_ast_node(statement, spaces_count)
            if (
                statement.node_type != NodeType.INLINE_ASSEMBLY
                and not result.endswith(";\n")
                and not result.endswith("}\n")
            ):
                result += (
                    f";{f' // {statement.comment.text}' if statement.comment else ''}\n"
                )

        else:
            result += parse_ast_node(statement, spaces_count)
    return result


def parse_ast_to_solidity(ast: SourceUnit) -> str:
    code = ""
    spaces_count = 0

    for node in ast.nodes:
        code += parse_ast_node(node, spaces_count)

    return code
