from typing import Dict, List, Optional, Union
import typing
from pydantic import BaseModel, Field
from solc_ast_parser.models.yul_models import YulBlock

from .base_ast_models import (
    Comment,
    ExpressionBase,
    MultilineComment,
    Node,
    NodeBase,
    NodeType,
    TypeBase,
    TypeDescriptions,
)

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
    "ModifierDefinition",
    "ModifierInvocation",
    "EventDefinition",
    "ErrorDefinition",
    "TypeName",
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
    "InlineAssembly",
    "Comment",
    "MultilineComment",
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

def build_function_header(node: ASTNode, spaces_count=0):
    name = f" {node.name}" if node.name else ""
    visibility = f" {node.visibility}"
    mutability = (
        f" {node.state_mutability}" if node.state_mutability != "nonpayable" else ""
    )

    overrides = " override" if node.overrides else ""
    virtual = " virtual" if node.virtual else ""
    return_params = node.return_parameters.parse()
    modifiers = (
        f" {', '.join([mod.parse() for mod in node.modifiers])}"
        if node.modifiers
        else ""
    )

    if return_params:
        return_params = f" returns ({return_params})"

    if node.kind == "constructor":
        return f"{' ' * spaces_count}constructor({node.parameters.parse()})"
    else:
        return f"{' ' * spaces_count}{node.kind}{name}({node.parameters.parse()}){visibility}{virtual}{mutability}{overrides}{modifiers}{return_params}"


class SourceUnit(NodeBase):
    license: Optional[str] = Field(default=None)
    nodes: List[ASTNode]
    experimental_solidity: Optional[bool] = Field(
        default=None, alias="experimentalSolidity"
    )
    exported_symbols: Optional[Dict[str, List[int]]] = Field(
        default=None, alias="exportedSymbols"
    )
    absolute_path: Optional[str] = Field(default=None, alias="absolutePath")

    def parse(self, spaces_count: int = 0):
        result = super().parse(spaces_count)
        for node in self.nodes:
            result += node.parse(spaces_count)

        return result


class PragmaDirective(NodeBase):
    literals: List[str]

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count)
        print(spaces_count)
        return (
            result
            + f"{' ' * spaces_count}pragma {self.literals[0]} {''.join(self.literals[1:])};\n\n"
        )


class ImportDirective(NodeBase):
    file: str
    source_unit: Optional[SourceUnit] = Field(default=None, alias="sourceUnit")
    scope: Optional[int] = Field(default=None)
    absolute_path: Optional[str] = Field(default=None, alias="absolutePath")
    unit_alias: Optional[str] = Field(default=None, alias="unitAlias")
    symbol_aliases: Optional[Dict] = Field(
        default=None, alias="symbolAliases"
    )  # TODO Check this type

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}import {self.absolute_path};"
        )


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

    def parse(self, spaces_count=0):
        base_contracts = ""
        if len(self.base_contracts):
            base_contracts = [base.parse() for base in self.base_contracts]
            base_contracts = f" is {', '.join(base_contracts)}"
        code = (
            super().parse(spaces_count)
            + f"{self.contract_kind} {self.name}{base_contracts} {{{f' // {self.comment.text}' if self.comment else ''}\n"
        )
        spaces_count = 4
        for contract_node in self.nodes:
            if contract_node.node_type == NodeType.VARIABLE_DECLARATION:
                code += f"{contract_node.parse(spaces_count)};{f' // {contract_node.comment.text}' if contract_node.comment else ''}\n"
                continue
            code += contract_node.parse(spaces_count)
        code += "}\n\n"

        return code


class IdentifierPath(NodeBase):
    name: str
    name_locations: List[str] = Field(alias="nameLocations")
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )

    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{' ' * spaces_count}{self.name}"


class InheritanceSpecifier(NodeBase):
    base_name: Union[IdentifierPath] = Field(alias="baseName")
    arguments: List[Expression] = Field(default_factory=list)

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count) + self.base_name.parse()
        if self.arguments:
            args = [arg.parse() for arg in self.arguments]
            result += f"({', '.join(args)})"
        return result


class FunctionNode(BaseModel, Node):
    function: Optional[IdentifierPath] = Field(default=None)
    definition: Optional[IdentifierPath] = Field(default=None)
    operator: Optional[str] = Field(default=None)

    def parse(self, spaces_count=0):
        return self.function.parse() if self.function else self.operator or ""


class UsingForDirective(NodeBase):
    type_name: Optional[TypeName] = Field(default=None, alias="typeName")
    library_name: Optional[IdentifierPath] = Field(default=None, alias="libraryName")
    global_: bool = Field(alias="global")
    function_list: Optional[List[FunctionNode]] = Field(
        default=None, alias="functionList"
    )

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count) + f"{' ' * spaces_count}using "

        if self.library_name:
            result += self.library_name.parse()

        if self.function_list:
            funcs = [f.parse() for f in self.function_list]
            result += f"{{{', '.join(funcs)}}}"

        result += " for "

        if self.type_name:
            result += self.type_name.parse()
        else:
            result += "*"

        if self.global_:
            result += " global"

        return result + ";\n"


class StructDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    visibility: str
    members: List["VariableDeclaration"]
    scope: Optional[int] = Field(default=None)
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")

    def parse(self, spaces_count=0):
        code = (
            super().parse(spaces_count) + f"{' ' * spaces_count}struct {self.name} {{\n"
        )
        spaces_count += 4
        for member in self.members:
            code += f"{' ' * spaces_count}{member.type_name.parse()} {member.name};\n"
        spaces_count -= 4

        code += f"{' ' * spaces_count}}}\n"
        return code


class EnumDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    members: List["EnumValue"]
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")

    def parse(self, spaces_count=0):
        result = (
            super().parse(spaces_count) + f"{' ' * spaces_count}enum {self.name} {{\n"
        )
        spaces_count += 4
        members = [f"{' ' * spaces_count}{member.name}" for member in self.members]
        result += ",\n".join(members)
        spaces_count -= 4
        result += f"\n{' ' * spaces_count}}}\n"
        return result


class EnumValue(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")

    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{' ' * spaces_count}{self.name}"


class UserDefinedValueTypeDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    underlying_type: TypeName = Field(alias="underlyingType")
    canonical_name: Optional[str] = Field(default=None, alias="canonicalName")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}struct {self.name} {{\n{' ' * spaces_count}}}\n"
        )


class ParameterList(NodeBase):
    parameters: List["VariableDeclaration"] = Field(default_factory=list)

    def parse(self, spaces_count=0):
        parsed = []
        for parameter in self.parameters:
            storage_location = (
                f" {parameter.storage_location}"
                if parameter.storage_location != "default"
                else ""
            )
            var_type = parameter.type_name.parse()
            name = f" {parameter.name}" if parameter.name else ""
            if parameter.node_type == NodeType.VARIABLE_DECLARATION:
                indexed = " indexed" if parameter.indexed else ""
            parsed.append(f"{var_type}{indexed}{storage_location}{name}")
        return super().parse() + ", ".join(parsed)


class OverrideSpecifier(NodeBase):
    overrides: List[IdentifierPath]

    def parse(self, spaces_count=0):
        if self.overrides:
            overrides = [f.name for f in self.overrides]
        return f"{' ' * spaces_count}override({', '.join(overrides)}) "


class FunctionDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    kind: Optional[str] = Field(default=None)
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
    base_functions: Optional[List[int]] = Field(default=None, alias="baseFunctions")

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count) + build_function_header(self, spaces_count)
        if not self.body:
            return result + ";\n\n"
        body = self.body.parse(spaces_count + 4)
        if body:
            result += f" {{\n{body}{' ' * spaces_count}}}\n\n"
        else:
            result += " {}\n\n"
        return result


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

    def parse(self, spaces_count=0):
        storage_location = (
            f" {self.storage_location}" if self.storage_location != "default" else ""
        )
        visibility = f" {self.visibility}" if self.visibility != "internal" else ""
        value = ""
        if self.value:
            value = f" = {self.value.parse()}"
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.type_name.parse()}{visibility}{storage_location} {self.name}{value}"
        )


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

    def parse(self, spaces_count=0):
        result = (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}modifier {self.name}({self.parameters.parse()}) {{\n"
        )
        spaces_count += 4
        result += self.body.parse(spaces_count)
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


class ModifierInvocation(NodeBase):
    modifier_name: IdentifierPath = Field(alias="modifierName")
    arguments: List[Expression] = Field(default_factory=list)
    kind: Optional[str] = Field(default=None)

    def parse(self, spaces_count=0):
        arguments = (
            f"({', '.join([arg.parse() for arg in self.arguments])})"
            if self.arguments
            else ""
        )
        return f"{' ' * spaces_count}{self.modifier_name.parse()}{arguments}"


class EventDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    parameters: ParameterList
    anonymous: bool
    event_selector: Optional[str] = Field(default=None, alias="eventSelector")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}event {self.name}({self.parameters.parse()});\n"
        )


class ErrorDefinition(NodeBase):
    name: str
    name_location: str = Field(alias="nameLocation")
    documentation: Optional["StructuredDocumentation"] = Field(default=None)
    parameters: ParameterList
    error_selector: Optional[str] = Field(default=None, alias="errorSelector")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}error {self.name}({self.parameters.parse()});\n"
        )


class ElementaryTypeName(TypeBase):
    name: str
    state_mutability: Optional[str] = Field(default=None, alias="stateMutability")

    def parse(self, spaces_count=0):
        if self.name == "address" and self.state_mutability == "payable":
            return (
                super().parse(spaces_count)
                + f"{' ' * spaces_count}{self.state_mutability}"
            )
        return super().parse(spaces_count) + f"{' ' * spaces_count}{self.name}"


class UserDefinedTypeName(TypeBase):
    path_node: IdentifierPath = Field(alias="pathNode")
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count) + f"{' ' * spaces_count}{self.path_node.name}"
        )


class FunctionTypeName(TypeBase):
    visibility: str
    state_mutability: str = Field(alias="stateMutability")
    parameter_types: List[ParameterList] = Field(alias="parameterTypes")
    return_parameter_types: List[ParameterList] = Field(alias="returnParameterTypes")

    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{build_function_header(self)};\n"


class Mapping(TypeBase):
    key_type: TypeName = Field(alias="keyType")
    key_name: str = Field(alias="keyName")
    key_name_location: str = Field(alias="keyNameLocation")
    value_type: TypeName = Field(alias="valueType")
    value_name: str = Field(alias="valueName")
    value_name_location: str = Field(alias="valueNameLocation")

    def parse(self, spaces_count=0):
        key_type = self.key_type.parse()
        value_type = self.value_type.parse()
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}mapping({key_type} => {value_type})"
        )


class ArrayTypeName(TypeBase):
    base_type: TypeName = Field(alias="baseType")
    length: Optional[Expression] = Field(default=None)

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.base_type.parse()}[{self.length or ''}]"
        )


class InlineAssembly(NodeBase):
    AST: YulBlock
    external_references: Optional[List[Dict]] = Field(
        default=None, alias="externalReferences"
    )
    evm_version: Optional[str] = Field(default=None, alias="evmVersion")
    eof_version: Optional[int] = Field(default=None, alias="eofVersion")
    flags: Optional[List[str]] = Field(default=None)

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}assembly {self.AST.parse(spaces_count)}"
        )


class Block(NodeBase):
    statements: List[Statement]

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count)
        for statement in self.statements:
            if not statement.node_type in (
                NodeType.COMMENT,
                NodeType.MULTILINE_COMMENT,
            ):
                result += statement.parse(spaces_count)
                if (
                    statement.node_type != NodeType.INLINE_ASSEMBLY
                    and not result.endswith(";\n")
                    and not result.endswith("}\n")
                ):
                    result += f";{f' // {statement.comment.text}' if statement.comment else ''}\n"

            else:
                result += statement.parse(spaces_count)
        return result


class PlaceholderStatement(NodeBase):

    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{' ' * spaces_count}_;\n"


class IfStatement(NodeBase):
    condition: Expression
    true_body: Statement = Field(alias="trueBody")
    false_body: Optional[Statement] = Field(default=None, alias="falseBody")

    def parse(self, spaces_count=0):
        result = (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}if ({self.condition.parse()}) {{\n"
        )
        spaces_count += 4
        result += self.true_body.parse(spaces_count)
        spaces_count -= 4

        if self.false_body:
            result += f"{' ' * spaces_count}}} else {{\n"
            spaces_count += 4
            result += self.false_body.parse(spaces_count)
            spaces_count -= 4

        result += f"{' ' * spaces_count}}}\n"
        return result


class TryCatchClause(NodeBase):
    error_name: str = Field(alias="errorName")
    parameters: Optional[ParameterList] = Field(default=None)
    block: Block

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count) + f"{' ' * spaces_count}catch "
        if self.parameters:
            result += f"({self.parameters.parse()}) "
        result += "{\n"
        spaces_count += 4
        result += self.block.parse(spaces_count)
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


class TryStatement(NodeBase):
    external_call: Optional[Expression] = Field(default=None, alias="externalCall")
    clauses: List[TryCatchClause]

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count) + f"{' ' * spaces_count}try "
        if self.external_call:
            result += self.external_call.parse()
        result += " {\n"

        for clause in self.clauses:
            result += clause.parse(spaces_count)

        result += f"{' ' * spaces_count}}}\n"
        return result


class WhileStatement(NodeBase):  # DoWhileStatement
    condition: Expression
    body: Statement

    def parse(self, spaces_count=0):
        result = (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}while ({self.condition.parse()}) {{\n"
        )
        spaces_count += 4
        result += self.body(spaces_count)
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


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

    def parse(self, spaces_count=0):
        result = super().parse(spaces_count) + f"{' ' * spaces_count}for ("
        if self.intialization_expression:
            result += f"{self.intialization_expression.parse()}; "
        if self.condition:
            result += f"{self.condition.parse()}; "
        if self.loop_expression:
            result += f"{self.loop_expression.parse()}"
        result += f") {{\n"
        spaces_count += 4
        result += self.body.parse(spaces_count)
        spaces_count -= 4
        result += f"{' ' * spaces_count}}}\n"
        return result


class Continue(NodeBase):
    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{' ' * spaces_count}continue"


class Break(NodeBase):
    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{' ' * spaces_count}break"


class Return(NodeBase):
    expression: Optional[Expression] = Field(default=None)
    function_return_parameters: Optional[int] = Field(
        default=None, alias="functionReturnParameters"
    )
    node_type: typing.Literal[NodeType.RETURN] = Field(alias="nodeType")

    class Config:
        extra = "forbid"

    def parse(self, spaces_count=0):
        if self.expression:
            return (
                super().parse(spaces_count)
                + f"{' ' * spaces_count}return {self.expression.parse()}"
            )
        else:
            return super().parse(spaces_count) + f"{' ' * spaces_count}return"


class Throw(NodeBase):
    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{' ' * spaces_count}throw;\n"


class EmitStatement(NodeBase):
    event_call: "FunctionCall" = Field(alias="eventCall")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * (spaces_count)}emit {self.event_call.parse()};\n"
        )


class RevertStatement(NodeBase):
    error_call: Optional["FunctionCall"] = Field(default=None, alias="errorCall")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}revert({self.error_call.parse()});\n"
        )


class VariableDeclarationStatement(NodeBase):
    assignments: List[Union[int, None]] = Field(default_factory=list)
    declarations: List[Union[VariableDeclaration, None]]
    initial_value: Optional[Expression] = Field(default=None, alias="initialValue")

    def parse(self, spaces_count=0):
        declarations = []
        for declaration in self.declarations:
            if declaration is None:
                declarations.append("")
            else:
                declarations.append(declaration.parse())
        if len(declarations) > 1:
            declarations_str = f"({', '.join(declarations)})"
        else:
            declarations_str = declarations[0]
        left = declarations_str
        right = f" = {self.initial_value.parse()}" if self.initial_value else ""
        return super().parse(spaces_count) + f"{' ' * (spaces_count)}{left}{right}"


class ExpressionStatement(NodeBase):
    expression: Expression

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * (spaces_count)}{self.expression.parse()}"
        )


class Conditional(ExpressionBase):  # TODO maybe errors
    condition: Expression
    true_expression: Expression = Field(alias="trueExpression")
    false_expression: Expression = Field(alias="falseExpression")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.condition.parse()} ? {self.true_expression.parse()} : {self.false_expression.parse()}"
        )


class Assignment(ExpressionBase):
    operator: str
    left_hand_side: Expression = Field(default=None, alias="leftHandSide")
    right_hand_side: Expression = Field(default=None, alias="rightHandSide")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.left_hand_side.parse()} {self.operator} {self.right_hand_side.parse()}"
        )


class TupleExpression(ExpressionBase):
    is_inline_array: bool = Field(alias="isInlineArray")
    components: List[Expression]

    def parse(self, spaces_count=0):
        res_tuple = [component.parse() for component in self.components]

        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}({', '.join(res_tuple)})"
        )


class UnaryOperation(ExpressionBase):
    prefix: bool
    operator: str
    sub_expression: Expression = Field(alias="subExpression")
    function: Optional[int] = Field(default=None)

    def parse(self, spaces_count=0):
        if self.prefix:
            return (
                super().parse(spaces_count)
                + f"{' ' * spaces_count}{self.operator}{self.sub_expression.parse()}"
            )
        else:
            return (
                super().parse(spaces_count)
                + f"{' ' * spaces_count}{self.sub_expression.parse()}{self.operator}"
            )


class BinaryOperation(ExpressionBase):
    operator: str
    left_expression: Expression = Field(alias="leftExpression")
    right_expression: Expression = Field(alias="rightExpression")
    common_type: TypeDescriptions = Field(alias="commonType")
    function: Optional[int] = Field(default=None)

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.left_expression.parse()} {self.operator} {self.right_expression.parse()}"
        )


class FunctionCall(ExpressionBase):
    expression: Expression
    names: List[str]
    name_locations: List[str] = Field(alias="nameLocations")
    arguments: List[Expression]
    try_call: bool = Field(alias="tryCall")
    kind: Optional[str] = Field(default=None)

    def parse(self, spaces_count=0):
        arguments = [arg.parse() for arg in self.arguments]
        if len(self.names) > 0:
            arguments = [f"{name}: {arg}" for name, arg in zip(self.names, arguments)]
            arguments_str = f"{{{', '.join(arguments)}}}"
        else:
            arguments_str = ", ".join(arguments)
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.expression.parse()}({arguments_str})"
        )


class FunctionCallOptions(ExpressionBase):
    expression: Expression
    names: List[str]
    options: List[Expression]

    def parse(self, spaces_count=0):
        options = [
            f"{name}: {option.parse()}"
            for name, option in zip(self.names, self.options)
        ]
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.expression.parse()}{{{' ,'.join(options)}}}"
        )


class NewExpression(ExpressionBase):
    type_name: TypeName = Field(alias="typeName")
    node_type: typing.Literal[NodeType.NEW_EXPRESSION] = Field(alias="nodeType")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}new {self.type_name.parse()}"
        )


class MemberAccess(ExpressionBase):
    member_name: str = Field(alias="memberName")
    member_location: str = Field(alias="memberLocation")
    expression: Expression
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.expression.parse()}.{self.member_name}"
        )


class IndexAccess(ExpressionBase):
    base_expression: Expression = Field(alias="baseExpression")
    index_expression: Optional[Expression] = Field(
        default=None, alias="indexExpression"
    )

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.base_expression.parse()}"
            + f"[{self.index_expression.parse() if self.index_expression else ''}]"
        )


class IndexRangeAccess(ExpressionBase):
    base_expression: Expression = Field(alias="baseExpression")
    start_expression: Optional[Expression] = Field(
        default=None, alias="startExpression"
    )
    end_expression: Optional[Expression] = Field(default=None, alias="endExpression")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.base_expression.parse()}"
            + f"[{self.start_expression.parse()}:{self.end_expression.parse()}]"
        )


class Identifier(TypeBase):
    name: str
    referenced_declaration: Optional[int] = Field(
        default=None, alias="referencedDeclaration"
    )
    overloaded_declarations: Optional[List[int]] = Field(
        default=None, alias="overloadedDeclarations"
    )

    def parse(self, spaces_count=0):
        return super().parse(spaces_count) + f"{' ' * spaces_count}{self.name}"


class ElementaryTypeNameExpression(ExpressionBase):
    type_name: ElementaryTypeName = Field(alias="typeName")

    def parse(self, spaces_count=0):
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.type_name.parse()}"
        )


class Literal(ExpressionBase):
    kind: Optional[str] = Field(default=None)
    value: str
    hex_value: str = Field(alias="hexValue")
    subdenomination: Optional[str] = Field(default=None)

    def parse(self, spaces_count=0):
        subdenomination = f" {self.subdenomination}" if self.subdenomination else ""
        if self.kind == "string":
            return f"{' ' * spaces_count}{repr(self.value)}{subdenomination}"
        return (
            super().parse(spaces_count)
            + f"{' ' * spaces_count}{self.value}{subdenomination}"
        )


class StructuredDocumentation(NodeBase):
    text: str  ## TODO CHECK THIS
