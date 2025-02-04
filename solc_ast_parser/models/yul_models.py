from typing import List, Optional, Union

from pydantic import Field
from solc_ast_parser.models.base_ast_models import YulBase

YulExpression = Union[
    "YulFunctionCall", "YulLiteral", "YulIdentifier", "YulBuiltinName"
]

YulStatement = Union[
    "YulExpressionStatement",
    "YulAssignment",
    "YulVariableDeclaration",
    "YulFunctionDefinition",
    "YulIf",
    "YulSwitch",
    "YulForLoop",
    "YulBreak",
    "YulContinue",
    "YulLeave",
    "YulBlock",
]

YulNode = Union["YulBlock", YulStatement, YulExpression]

class YulBlock(YulBase):
    statements: List[YulStatement]


class YulTypedName(YulBase):
    name: str
    type: str


class YulLiteral(YulBase):
    kind: str
    hex_value: Optional[str] = Field(default=None, alias="hexValue")
    type: str
    value: str


class YulIdentifier(YulBase):
    name: str


class YulBuiltinName(YulBase):
    name: str


class YulAssignment(YulBase):
    variable_names: List[YulIdentifier] = Field(alias="variableNames")
    value: Optional[YulExpression] = Field(default=None)


class YulFunctionCall(YulBase):
    function_name: YulIdentifier = Field(alias="functionName")
    arguments: List[YulExpression]


class YulExpressionStatement(YulBase):
    expression: YulExpression


class YulVariableDeclaration(YulBase):
    variables: List[YulTypedName] 
    value: Optional[YulExpression] = Field(default=None)


class YulFunctionDefinition(YulBase):
    name: str
    parameters: List[YulTypedName] = Field(default=None)
    return_variables: List[YulTypedName] = Field(default=None)
    body: YulBlock


class YulIf(YulBase):
    condition: YulExpression
    body: YulBlock


class YulCase(YulBase):
    value: str
    body: YulBlock


class YulSwitch(YulBase):
    expression: YulExpression
    cases: List[YulCase]


class YulForLoop(YulBase):
    pre: YulBlock
    condition: YulExpression
    post: YulBlock
    body: YulBlock


class YulBreak(YulBase):
    pass


class YulContinue(YulBase):
    pass


class YulLeave(YulBase):
    pass
