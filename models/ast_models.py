import enum
from typing import Dict, List, Optional, TypeAlias, Union
from pydantic import BaseModel, Field

from models.base_ast_models import ExpressionBase, NodeBase, TypeBase, TypeDescriptions


ASTNode = Union[
    "PragmaDirective",
    "ImportDirective",
    "ContractDefinition",
    "SourceUnit",
    "StructuredDocumentation",
    "IdentifierPath",
    "InheritanceSpecifier",
    "UsingForDirective",
    "StructDefinition",
    "EnumDefinition",
    "EnumValue",
    "UserDefinedValueTypeDefinition",
    "ParameterList",
    "CallableDeclaration",
    "OverrideSpecifier",
    "FunctionDefinition",
    "VariableDeclaration",
    "ModifierDefinition",
    "ModifierInvocation",
    "EventDefinition",
    "ErrorDefinition",
    "MagicVariableDeclaration",
    "TypeName",
    "ElementaryTypeName",
    "UserDefinedTypeName",
    "FunctionTypeName",
    "Mapping",
    "ArrayTypeName",
    "InlineAssembly",
    "Block",
    "PlaceholderStatement",
    "IfStatement",
    "TryCatchClause",
    "TryStatement",
    "BreakableStatement",
    "ForStatement",
    "Continue",
    "Return",
    "Throw",
    "RevertStatement",
    "EmitStatement",
    "VariableDeclarationStatement",
    "ExpressionStatement",
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
    "Identifier",
    "ElementaryTypeNameExpression",
    "Literal",
    "TypeClassDefinition",
    "TypeClassInstantation",
    "TypeDefinition",
    "TypeClassName",
    "Builtin",
    "ForAllQuantifier",
]


class PragmaDirective(NodeBase):
    tokens: Optional[List[int]] = Field(default=None)
    literals: List[str]


class ImportDirective(NodeBase):
    symbol: "Identifier"
    alias: Optional[str] = Field(default=None)


class StructuredDocumentation(NodeBase):
    text: str


class ContractDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional[StructuredDocumentation] = Field(default=None)
    contract_kind: str = Field(alias="contractKind")
    abstract: bool
    base_contracts: List["InheritanceSpecifier"] = Field(alias="baseContracts")
    contract_dependencies: List[int] = Field(alias="contractDependencies")
    used_events: List[int] = Field(alias="usedEvents")
    used_errors: List = Field(alias="usedErrors")
    nodes: List[ASTNode]
    scope: int
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")
    fully_implemented: Optional[bool] = Field(default=None, alias="fullyImplemented")
    linearized_base_contracts: Optional[Dict] = Field(default=None, alias="linearizedBaseContracts")
    internal_function_ids: Optional[Dict] = Field(default=None,alias="internalFunctionIDs")


class IdentifierPath(NodeBase):
    path: List[str]
    path_locations: List[str] = Field(alias="pathLocations")


class InheritanceSpecifier(NodeBase):
    arguments: List[int]
    base_name: Union[IdentifierPath] = Field(alias="baseName")


DefaultMember = Union[
    "Identifier",
    "Literal",
    "UnaryOperation",
    "BinaryOperation",
    "MemberAccess",
    "IndexAccess",
]


class ElementaryTypeName(TypeBase):
    name: str
    state_mutability: Optional[str] = Field(default=None, alias="stateMutability")


class PathNode(NodeBase):
    name: str
    name_locations: List[str] = Field(alias="nameLocations")
    node_type: str = Field(alias="nodeType")
    referenced_declaration: int = Field(alias="referencedDeclaration")


class UserDefinedTypeName(TypeBase):
    path_node: PathNode = Field(alias="pathNode")
    referenced_declaration: int = Field(alias="referencedDeclaration")


class Mapping(TypeBase):
    key_name: str = Field(alias="keyName")
    key_name_location: str = Field(alias="keyNameLocation")
    key_type: Union[UserDefinedTypeName, ElementaryTypeName, "Mapping"] = Field(
        alias="keyType"
    )
    value_name: str = Field(alias="valueName")
    value_name_location: str = Field(alias="valueNameLocation")
    value_type: Union[UserDefinedTypeName, ElementaryTypeName, "Mapping"] = Field(
        alias="valueType"
    )


class VariableDeclaration(TypeBase):
    constant: bool
    function_selector: Optional[str] = Field(default=None, alias="functionSelector")
    mutability: str
    indexed: Optional[bool] = Field(default=None)
    name: str
    name_location: Optional[str] = Field(alias="nameLocation")
    value: Optional[DefaultMember] = Field(default=None)
    scope: int
    state_variable: bool = Field(alias="stateVariable")
    storage_location: str = Field(alias="storageLocation")
    type_name: Union[Mapping, ElementaryTypeName, UserDefinedTypeName] = Field(
        alias="typeName"
    )
    visibility: str


class ParameterList(NodeBase):
    parameters: List[VariableDeclaration]


class Identifier(TypeBase):
    name: str
    overloaded_declarations: List[int] = Field(alias="overloadedDeclarations")
    referenced_declaration: int = Field(alias="referencedDeclaration")


class Literal(ExpressionBase):
    hex_value: str = Field(alias="hexValue")
    subdenomination: Optional[str] = Field(default=None)
    kind: str
    value: str


class UnaryOperation(ExpressionBase):
    operator: str
    prefix: bool
    sub_expression: DefaultMember = Field(alias="subExpression")


class BinaryOperation(ExpressionBase):
    common_type: TypeDescriptions = Field(alias="commonType")
    left_expression: Union[
        DefaultMember,
        "TupleExpression",
        "FunctionCall",
    ] = Field(alias="leftExpression")
    operator: str
    right_expression: Union[
        DefaultMember,
        "TupleExpression",
        "FunctionCall",
    ] = Field(alias="rightExpression")


class Return(NodeBase):
    function_return_parameters: int = Field(alias="functionReturnParameters")
    expression: Union[Identifier, Literal]


class MemberAccess(ExpressionBase):
    expression: Union[DefaultMember, "FunctionCall"]
    member_location: str = Field(alias="memberLocation")
    member_name: str = Field(alias="memberName")
    sub_expression: Optional[Identifier] = Field(default=None, alias="subExpression")


class IndexAccess(ExpressionBase):
    base_expression: Union[Identifier, "IndexAccess", MemberAccess] = Field(
        alias="baseExpression"
    )
    index_expression: Union[MemberAccess, Identifier, Literal, "IndexAccess"] = Field(
        alias="indexExpression"
    )


class FunctionCall(ExpressionBase):
    arguments: List[Union[DefaultMember, "FunctionCall"]]
    expression: Union[
        Identifier, MemberAccess, IndexAccess, "ElementaryTypeNameExpression"
    ]
    kind: str
    name_locations: List[str] = Field(alias="nameLocations")
    names: List[str]
    try_call: bool = Field(alias="tryCall")


class FunctionCallOptions(ExpressionBase):
    argument_types: List[TypeDescriptions] = Field(alias="argumentTypes")
    expression: Union[Identifier, MemberAccess, IndexAccess] = Field()
    names: List[str]
    options: List[DefaultMember]


class EmitStatement(NodeBase):
    event_call: FunctionCall = Field(alias="eventCall")


class Assignment(ExpressionBase):
    left_hand_side: Optional[Union[Identifier, MemberAccess, IndexAccess]] = Field(
        default=None, alias="leftHandSide"
    )
    operator: str
    right_hand_side: Union[DefaultMember, FunctionCall, "TupleExpression"] = Field(
        default=None, alias="rightHandSide"
    )


class ElementaryTypeNameExpression(ExpressionBase):
    type_name: ElementaryTypeName = Field(alias="typeName")
    argument_types: List[TypeDescriptions] = Field(alias="argumentTypes")


class TupleExpression(ExpressionBase):
    is_inline_array: bool = Field(alias="isInlineArray")
    components: List[DefaultMember]


class VariableDeclarationStatement(NodeBase):
    assignments: List[int]
    declarations: List[VariableDeclaration]
    initial_value: Union[IndexAccess, MemberAccess, FunctionCall] = Field(
        alias="initialValue"
    )


Expression = Union[
    Assignment,
    UnaryOperation,
    IndexAccess,
    BinaryOperation,
    FunctionCall,
    TupleExpression,
    VariableDeclarationStatement,
    FunctionCallOptions,
]


class ExpressionStatement(NodeBase):
    expression: Expression


class Block(NodeBase):
    statements: List[
        Union[
            ExpressionStatement,
            Return,
            EmitStatement,
            FunctionCall,
            VariableDeclarationStatement,
        ]
    ]


class FunctionDefinition(NodeBase):
    body: Block
    function_selector: Optional[str] = Field(default=None, alias="functionSelector")
    implemented: bool = True
    kind: str
    modifiers: List = Field(default_factory=list)
    name_location: str = Field(alias="nameLocation")
    parameters: ParameterList
    return_parameters: ParameterList = Field(alias="returnParameters")
    scope: int
    name: str
    state_mutability: str = Field(alias="stateMutability")
    virtual: bool = False
    visibility: str


class StructDefinition(NodeBase):
    canonical_name: str = Field(alias="canonicalName")
    members: List[VariableDeclaration | FunctionDefinition]
    name_location: str = Field(alias="nameLocation")
    scope: int
    name: str
    visibility: str


class EventDefinition(NodeBase):
    anonymous: bool
    event_selector: str = Field(alias="eventSelector")
    name_location: str = Field(alias="nameLocation")
    parameters: ParameterList
    name: str


class SourceUnit(NodeBase):
    license: Optional[str] = Field(default=None)
    absolute_path: str = Field(alias="absolutePath")
    exported_symbols: Dict[str, List[int]] = Field(alias="exportedSymbols")
    nodes: List[Union[ContractDefinition, PragmaDirective]]
