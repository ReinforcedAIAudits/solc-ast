import enum
from typing import Dict, List, Optional, TypeAlias, Union
from pydantic import BaseModel, Field

from .base_ast_models import ExpressionBase, NodeBase, TypeBase, TypeDescriptions

ASTNode = Union[
    "PragmaDirective",
    "SourceUnit",
    "StructuredDocumentation",
    "IdentifierPath",
    "InheritanceSpecifier",
    "UsingForDirective",
    "ParameterList",
    "OverrideSpecifier",
    "FunctionDefinition",
    "FunctionNode",
    "ModifierDefinition",
    "ModifierInvocation",
    "EventDefinition",
    "ErrorDefinition",
    "TypeName",
    # "InlineAssembly",
    "TryCatchClause",
    "Expression",
    "Declaration",
    "Statement",
]

Statement = Union[
    "Block",
    "PlaceholderStatement",
    "IfStatement",
    "TryStatement",
    "ForStatement",
    "Continue",
    "Break",
    "Return",
    "Throw",
    "RevertStatement",
    "EmitStatement",
    "VariableDeclarationStatement",
    "ExpressionStatement",
]

Declaration = Union[
    "ImportDirective",
    "ContractDefinition",
    "StructDefinition",
    "EnumDefinition",
    "EnumValue",
    "UserDefinedValueTypeDefinition",
    "VariableDeclaration",
]

Expression = Union[
    "Conditional",
    "Assignment",
    "TupleExpression",
    "UnaryOperation",
    "BinaryOperation",
    "FunctionCall",
    "FunctionCallOptions",
    "NewExpression",
    "MemberAccess",
    "IndexAccess",
    "IndexRangeAccess",
    "PrimaryExpression",
]

PrimaryExpression = Union[
    "Literal",
    "Identifier",
    "ElementaryTypeNameExpression",
]

TypeName = Union[
    "ElementaryTypeName",
    "UserDefinedTypeName",
    "FunctionTypeName",
    "Mapping",
    "ArrayTypeName",
]


class SourceUnit(NodeBase):
    license: Optional[str] = Field(default=None)
    nodes: List[ASTNode]
    experimental_solidity: Optional[bool] = Field(
        default=None, alias="experimentalSolidity"
    )
    exported_symbols: Dict[str, List[int]] = Field(alias="exportedSymbols")
    absolute_path: Optional[str] = Field(default=None, alias="absolutePath")


class PragmaDirective(NodeBase):
    literals: List[str]


class ImportDirective(NodeBase):
    file: str
    source_unit: Optional[SourceUnit] = Field(default=None, alias="sourceUnit")
    scope: Optional[int] = Field(default=None)
    absolute_path: Optional[str] = Field(default=None, alias="absolutePath")
    unit_alias: Optional[str] = Field(default=None, alias="unitAlias")
    symbol_aliases: Optional[Dict] = Field(
        default=None, alias="symbolAliases"
    )  # TODO Check this type


class ContractDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    contract_kind: str = Field(alias="contractKind")
    abstract: bool
    base_contracts: List["InheritanceSpecifier"] = Field(alias="baseContracts")
    contract_dependencies: List[int] = Field(alias="contractDependencies")
    used_events: List[int] = Field(alias="usedEvents")
    used_errors: List = Field(alias="usedErrors")
    nodes: List[ASTNode]
    scope: Optional[int] = Field(default=None)
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")
    fully_implemented: Optional[bool] = Field(default=None, alias="fullyImplemented")
    linearized_base_contracts: Optional[List] = Field(
        default=None, alias="linearizedBaseContracts"
    )  # TODO: Check this type
    internal_function_ids: Optional[List] = Field(
        default=None, alias="internalFunctionIDs"
    )  # TODO: Check this type


class IdentifierPath(NodeBase):
    name: str
    name_locations: List[str] = Field(alias="nameLocations")
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )


class InheritanceSpecifier(NodeBase):
    base_name: Union[IdentifierPath] = Field(alias="baseName")
    arguments: List[Expression] = Field(default_factory=list)


class FunctionNode(BaseModel):
    function: Optional[IdentifierPath] = Field(default=None)
    definition: Optional[IdentifierPath] = Field(default=None)
    operator: Optional[str] = Field(default=None)


class UsingForDirective(NodeBase):
    type_name: Optional[TypeName] = Field(default=None, alias="typeName")
    library_name: Optional[IdentifierPath] = Field(default=None, alias="libraryName")
    global_: bool = Field(alias="global")
    function_list: Optional[List[FunctionNode]] = Field(
        default=None, alias="functionList"
    )


class StructDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    visibility: str
    members: List["VariableDeclaration"]
    scope: Optional[int] = Field(default=None)
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")


class EnumDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    members: List["EnumValue"]
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")


class EnumValue(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")


class UserDefinedValueTypeDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    underlying_type: TypeName = Field(alias="underlyingType")
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")


class ParameterList(NodeBase):
    parameters: List["VariableDeclaration"] = Field(default_factory=list)


class OverrideSpecifier(NodeBase):
    overrides: List[IdentifierPath]


class FunctionDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    kind: str
    state_mutability: str = Field(alias="stateMutability")
    virtual: bool = Field(default=False)
    overrides: Optional[OverrideSpecifier] = Field(default=None)
    parameters: ParameterList
    return_parameters: ParameterList = Field(alias="returnParameters")
    modifiers: List["ModifierInvocation"] = Field(default_factory=list)
    body: Optional["Block"] = Field(default=None)
    implemented: bool
    scope: Optional[int] = Field(default=None)
    visibility: Optional[str] = Field(default=None)
    function_selector: Optional[str] = Field(default=None, alias="functionSelector")
    base_functions: Optional[Dict] = Field(
        default=None, alias="baseFunctions"
    )  # TODO: Check this type


class VariableDeclaration(TypeBase):
    name: str
    name_location: Optional[str] = Field(alias="nameLocation")
    type_name: TypeName = Field(alias="typeName")
    constant: bool
    mutability: str
    state_variable: bool = Field(alias="stateVariable")
    storage_location: str = Field(alias="storageLocation")
    overrides: Optional[OverrideSpecifier] = Field(default=None)
    visibility: str
    value: Optional[Expression] = Field(default=None)
    scope: Optional[int] = Field(default=None)
    function_selector: Optional[str] = Field(default=None, alias="functionSelector")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    indexed: Optional[bool] = Field(default=None)
    base_functions: Optional[Dict] = Field(
        default=None, alias="baseFunctions"
    )  # TODO: Check this type


class ModifierDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    visibility: str
    parameters: ParameterList
    virtual: bool
    overrides: Optional[OverrideSpecifier] = Field(default=None)
    body: Optional["Block"] = Field(default=None)
    base_modifiers: Optional[Dict] = Field(
        default=None, alias="baseModifiers"
    )  # TODO: Check this type


class ModifierInvocation(NodeBase):
    modifier_name: IdentifierPath = Field(alias="modifierName")
    arguments: List[Expression] = Field(default_factory=list)
    kind: Optional[str]


class EventDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    parameters: ParameterList
    anonymous: bool
    event_selector: Optional[str] = Field(default=None, alias="eventSelector")


class ErrorDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    parameters: ParameterList
    error_selector: Optional[str] = Field(default=None, alias="errorSelector")


class ElementaryTypeName(TypeBase):
    name: str
    state_mutability: Optional[str] = Field(default=None, alias="stateMutability")


class UserDefinedTypeName(TypeBase):
    path_node: IdentifierPath = Field(alias="pathNode")
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )


class FunctionTypeName(TypeBase):
    visibility: str
    state_mutability: str = Field(alias="stateMutability")
    parameter_types: List[ParameterList] = Field(alias="parameterTypes")
    return_parameter_types: List[ParameterList] = Field(alias="returnParameterTypes")


class Mapping(TypeBase):
    key_type: TypeName = Field(alias="keyType")
    key_name: str = Field(alias="keyName")
    key_name_location: str = Field(alias="keyNameLocation")
    value_type: TypeName = Field(alias="valueType")
    value_name: str = Field(alias="valueName")
    value_name_location: str = Field(alias="valueNameLocation")


class ArrayTypeName(TypeBase):
    base_type: TypeName = Field(alias="baseType")
    length: Optional[Expression] = Field(default=None)


# TODO InlineAssembly


class Block(NodeBase):
    statements: List[Statement]


class PlaceholderStatement(NodeBase):
    pass


class IfStatement(NodeBase):
    condition: Expression
    true_body: Statement = Field(alias="trueBody")
    false_body: Optional[Statement] = Field(default=None, alias="falseBody")


class TryCatchClause(NodeBase):
    error_name: str = Field(alias="errorName")
    parameters: Optional[ParameterList] = Field(default=None)
    block: Block


class TryStatement(NodeBase):
    external_call: Optional[Expression] = Field(default=None, alias="externalCall")
    clauses: List[TryCatchClause]


class WhileStatement(NodeBase):  # DoWhileStatement
    condition: Expression
    body: Statement


class ForStatement(NodeBase):
    intialization_expression: Optional[Statement] = Field(
        default=None, alias="initializationExpression"
    )
    condition: Optional[Expression] = Field(default=None)
    loop_expression: Optional["ExpressionStatement"] = Field(
        default=None, alias="loopExpression"
    )
    body: Statement
    is_simple_counter_loop: Optional[bool] = Field(
        default=None, alias="isSimpleCounterLoop"
    )


class Continue(NodeBase):
    pass


class Break(NodeBase):
    pass


class Return(NodeBase):
    expression: Optional[Expression] = Field(default=None)
    function_return_parameters: Optional[int] = Field(
        default=None, alias="functionReturnParameters"
    )


class Throw(NodeBase):
    pass


class EmitStatement(NodeBase):
    event_call: "FunctionCall" = Field(alias="eventCall")


class RevertStatement(NodeBase):
    error_call: Optional["FunctionCall"] = Field(default=None, alias="errorCall")


class VariableDeclarationStatement(NodeBase):
    assignments: List[Union[int, None]] = Field(default_factory=list)
    declarations: List[Union[VariableDeclaration, None]]
    initial_value: Expression = Field(alias="initialValue")


class ExpressionStatement(NodeBase):
    expression: Expression


class Conditional(ExpressionBase):  # TODO maybe errors
    condition: Expression
    true_expression: Expression = Field(alias="trueExpression")
    false_expression: Expression = Field(alias="falseExpression")


class Assignment(ExpressionBase):
    operator: str
    left_hand_side: Expression = Field(default=None, alias="leftHandSide")
    right_hand_side: Expression = Field(default=None, alias="rightHandSide")


class TupleExpression(ExpressionBase):
    is_inline_array: bool = Field(alias="isInlineArray")
    components: List[Expression]


class UnaryOperation(ExpressionBase):
    prefix: bool
    operator: str
    sub_expression: Expression = Field(alias="subExpression")
    function: Optional[int] = Field(default=None)


class BinaryOperation(ExpressionBase):
    operator: str
    left_expression: Expression = Field(alias="leftExpression")
    right_expression: Expression = Field(alias="rightExpression")
    common_type: TypeDescriptions = Field(alias="commonType")
    function: Optional[int] = Field(default=None)


class FunctionCall(ExpressionBase):
    expression: Expression
    names: List[str]
    name_locations: List[str] = Field(alias="nameLocations")
    arguments: List[Expression]
    try_call: bool = Field(alias="tryCall")
    kind: str


class FunctionCallOptions(ExpressionBase):
    expression: Expression
    names: List[str]
    options: List[Expression]


class NewExpression(ExpressionBase):
    type_name: TypeName = Field(alias="typeName")


class MemberAccess(ExpressionBase):
    member_name: str = Field(alias="memberName")
    member_location: str = Field(alias="memberLocation")
    expression: Expression
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )


class IndexAccess(ExpressionBase):
    base_expression: Expression = Field(alias="baseExpression")
    index_expression: Expression = Field(alias="indexExpression")


class IndexRangeAccess(ExpressionBase):
    base_expression: Expression = Field(alias="baseExpression")
    start_expression: Optional[Expression] = Field(
        default=None, alias="startExpression"
    )
    end_expression: Optional[Expression] = Field(default=None, alias="endExpression")


class Identifier(TypeBase):
    name: str
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )
    overloaded_declarations: Optional[List[int]] = Field(
        default=None, alias="overloadedDeclarations"
    )


class ElementaryTypeNameExpression(ExpressionBase):
    type_name: ElementaryTypeName = Field(alias="typeName")


class Literal(ExpressionBase):
    kind: str
    value: str
    hex_value: str = Field(alias="hexValue")
    subdenomination: Optional[str] = Field(default=None)


class StructuredDocumentation(NodeBase):
    text: str  ## TODO CHECK THIS
