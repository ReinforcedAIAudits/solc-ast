import enum
from typing import Optional, Union
from pydantic import BaseModel, Field


class NodeType(enum.StrEnum):
    SOURCE_UNIT = "SourceUnit"
    BLOCK = "Block"
    PRAGMA_DIRECTIVE = "PragmaDirective"
    CONTRACT_DEFINITION = "ContractDefinition"
    FUNCTION_DEFINITION = "FunctionDefinition"
    VARIABLE_DECLARATION = "VariableDeclaration"
    VARIABLE_DECLARATION_STATEMENT = "VariableDeclarationStatement"
    FUNCTION_CALL = "FunctionCall"
    PARAMETER_LIST = "ParameterList"
    EVENT_DEFINITION = "EventDefinition"
    EMIT_STATEMENT = "EmitStatement"
    ASSIGNMENT = "Assignment"
    BINARY_OPERATION = "BinaryOperation"
    UNARY_OPERATION = "UnaryOperation"
    LITERAL = "Literal"
    IDENTIFIER = "Identifier"
    IDENTIFIER_PATH = "IdentifierPath"
    MEMBER_ACCESS = "MemberAccess"
    INDEX_ACCESS = "IndexAccess"
    TUPLE_EXPRESSION = "TupleExpression"
    EXPRESSION_STATEMENT = "ExpressionStatement"
    RETURN = "Return"
    ELEMENTARY_TYPE_NAME = "ElementaryTypeName"
    USER_DEFINED_TYPE_NAME = "UserDefinedTypeName"
    STRUCT_DEFINITION = "StructDefinition"
    MAPPING = "Mapping"
    ELEMENTARY_TYPE_NAME_EXPRESSION = "ElementaryTypeNameExpression"
    


class TypeDescriptions(BaseModel):
    type_identifier: Optional[str] = Field(default=None, alias="typeIdentifier")
    type_string: Optional[str] = Field(default=None, alias="typeString")


class NodeBase(BaseModel):
    id: int
    src: str
    node_type: NodeType = Field(alias="nodeType")


class TypeBase(NodeBase):
    type_descriptions: TypeDescriptions = Field(alias="typeDescriptions")


class ExpressionBase(TypeBase):
    is_constant: bool = Field(alias="isConstant")
    is_lvalue: bool = Field(alias="isLValue")
    is_pure: bool = Field(alias="isPure")
    lvalue_requested: bool = Field(alias="lValueRequested")
