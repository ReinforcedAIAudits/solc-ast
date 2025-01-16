import enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class NodeType(enum.StrEnum):
    SOURCE_UNIT = "SourceUnit"
    BLOCK = "Block" 
    PRAGMA_DIRECTIVE = "PragmaDirective"
    CONTRACT_DEFINITION = "ContractDefinition"
    FUNCTION_DEFINITION = "FunctionDefinition"
    FUNCTION_NODE = "FunctionNode"
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
    INDEX_RANGE_ACCESS = "IndexRangeAccess"
    TUPLE_EXPRESSION = "TupleExpression"
    EXPRESSION_STATEMENT = "ExpressionStatement"
    RETURN = "Return"
    ELEMENTARY_TYPE_NAME = "ElementaryTypeName"
    USER_DEFINED_TYPE_NAME = "UserDefinedTypeName"
    STRUCT_DEFINITION = "StructDefinition"
    MAPPING = "Mapping"
    ELEMENTARY_TYPE_NAME_EXPRESSION = "ElementaryTypeNameExpression"
    INHERITANCE_SPECIFIER = "InheritanceSpecifier"
    USING_FOR_DIRECTIVE = "UsingForDirective"
    STRUCTURED_DOCUMENTATION = "StructuredDocumentation"
    MODIFIER_DEFINITION = "ModifierDefinition"
    MODIFIER_INVOCATION = "ModifierInvocation"
    ERROR_DEFINITION = "ErrorDefinition"
    PLACEHOLDER_STATEMENT = "PlaceholderStatement"
    IF_STATEMENT = "IfStatement"
    TRY_CATCH_CLAUSE = "TryCatchClause"
    TRY_STATEMENT = "TryStatement"
    FOR_STATEMENT = "ForStatement"
    CONTINUE = "Continue"
    BREAK = "Break"
    THROW = "Throw"
    REVERT_STATEMENT = "RevertStatement"
    FUNCTION_CALL_OPTIONS = "FunctionCallOptions"
    NEW_EXPRESSION = "NewExpression"
    CONDITIONAL = "Conditional"
    IMPORT_DIRECTIVE = "ImportDirective"
    ENUM_DEFINITION = "EnumDefinition"
    ENUM_VALUE = "EnumValue"
    USER_DEFINED_VALUE_TYPE_DEFINITION = "UserDefinedValueTypeDefinition"
    FUNCTION_TYPE_NAME = "FunctionTypeName"
    ARRAY_TYPE_NAME = "ArrayTypeName"
    OVERRIDE_SPECIFIER = "OverrideSpecifier"    


class TypeDescriptions(BaseModel):
    type_identifier: Optional[str] = Field(default=None, alias="typeIdentifier")
    type_string: Optional[str] = Field(default=None, alias="typeString")


class NodeBase(BaseModel):
    id: int
    src: str
    node_type: NodeType = Field(alias="nodeType")

    class Config:
        extra = 'forbid'


class TypeBase(NodeBase):
    type_descriptions: Optional[TypeDescriptions] = Field(default=None, alias="typeDescriptions")
    argument_types: Optional[List[TypeDescriptions]] = Field(default=None, alias="argumentTypes")



class ExpressionBase(TypeBase):
    is_constant: bool = Field(alias="isConstant")
    is_lvalue: bool = Field(alias="isLValue")
    is_pure: bool = Field(alias="isPure")
    lvalue_requested: bool = Field(alias="lValueRequested")
