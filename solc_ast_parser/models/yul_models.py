from typing import List, Optional, Union

from pydantic import Field
from solc_ast_parser.models.base_ast_models import YulBase, YulNodeType

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

    def parse(self, spaces_count=0, new_line: bool = False):
        if len(self.statements) == 1 and not new_line:
            return f"{{ {self.statements[0].parse()} }}\n"

        if not self.statements:
            return "{ }\n"

        statements = "\n".join(
            [statement.parse(spaces_count + 4) for statement in self.statements]
        )
        return f"{{\n{statements}\n{' ' * spaces_count}}}\n"


class YulTypedName(YulBase):
    name: str
    type: str

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line) + f"{' ' * spaces_count}{self.name}"
        )


class YulLiteral(YulBase):
    kind: str
    hex_value: Optional[str] = Field(default=None, alias="hexValue")
    type: str
    value: str

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line) + f"{' ' * spaces_count}{self.value}"
        )


class YulIdentifier(YulBase):
    name: str

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line) + f"{' ' * spaces_count}{self.name}"
        )


class YulBuiltinName(YulBase):
    name: str

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line) + f"{' ' * spaces_count}{self.name}"
        )


class YulAssignment(YulBase):
    variable_names: List[YulIdentifier] = Field(alias="variableNames")
    value: Optional[YulExpression] = Field(default=None)

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}{', '.join([var.parse() for var in self.variable_names])} := {self.value.parse()}"
        )


class YulFunctionCall(YulBase):
    function_name: YulIdentifier = Field(alias="functionName")
    arguments: List[YulExpression]

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}{self.function_name.parse(spaces_count)}"
            + f"({', '.join([arg.parse() for arg in self.arguments])})"
        )


class YulExpressionStatement(YulBase):
    expression: YulExpression

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}{self.expression.parse( spaces_count)}"
        )


class YulVariableDeclaration(YulBase):
    variables: List[YulTypedName]
    value: Optional[YulExpression] = Field(default=None)

    def parse(self, spaces_count=0, new_line=False):
        value = f" := {self.value.parse( spaces_count)}" if self.value else ""
        variables = ",".join([var.parse(spaces_count) for var in self.variables])
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}{variables}{value}"
        )


class YulFunctionDefinition(YulBase):
    name: str
    parameters: List[YulTypedName] = Field(default=None)
    return_variables: List[YulTypedName] = Field(default=None)
    body: YulBlock

    def parse(self, spaces_count=0, new_line=False):
        parameters = ", ".join([param.parse() for param in self.parameters])
        return_variables = ", ".join(
            [return_variable.parse() for return_variable in self.return_variables]
        )
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}function {self.name}({parameters}) -> {return_variables} {self.body.parse()}"
        )


class YulIf(YulBase):
    condition: YulExpression
    body: YulBlock

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}if {self.condition.parse()} {self.body.parse( spaces_count, True)}"
        )


class YulCase(YulBase):
    value: str
    body: YulBlock

    def parse(self, spaces_count=0, new_line=False):
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}case {self.value} {self.body.parse( spaces_count=0, new_line=True)}"
        )


class YulSwitch(YulBase):
    expression: YulExpression
    cases: List[YulCase]

    def parse(self, spaces_count=0, new_line=False):
        cases = "\n".join([case.parse(spaces_count) for case in self.cases])
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}switch {self.expression.parse()} {cases}"
        )


class YulForLoop(YulBase):
    pre: YulBlock
    condition: YulExpression
    post: YulBlock
    body: YulBlock

    def parse(self, spaces_count=0, new_line=False):
        pre_arr = []
        for statement in self.pre.statements:
            if statement.node_type == YulNodeType.YUL_VARIABLE_DECLARATION:
                pre_arr.append(f"let {statement.parse()}")
            else:
                pre_arr.append(statement.parse())
        return (
            super().parse(spaces_count, new_line)
            + f"{' ' * spaces_count}for {{ {', '.join(pre_arr)} }} {self.condition.parse()} {self.post.parse()} {self.body.parse( spaces_count, True)}"
        )


class YulBreak(YulBase):
    def parse(self, spaces_count=0, new_line=False):
        return super().parse(spaces_count, new_line) + f"{' ' * spaces_count}break"


class YulContinue(YulBase):
    def parse(self, spaces_count=0, new_line=False):
        return super().parse(spaces_count, new_line) + f"{' ' * spaces_count}continue"


class YulLeave(YulBase):
    def parse(self, spaces_count=0, new_line=False):
        return super().parse(spaces_count, new_line) + f"{' ' * spaces_count}leave"
