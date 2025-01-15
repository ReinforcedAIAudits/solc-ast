from enum import Enum
import json
from typing import Union, Mapping, List, Optional
from dataclasses import dataclass
from ast_parser import parse_ast_to_solidity
import solcx

from models.ast_models import (
    Assignment,
    BinaryOperation,
    Block,
    ElementaryTypeName,
    EventDefinition,
    ExpressionStatement,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    IndexAccess,
    MemberAccess,
    ParameterList,
    PragmaDirective,
    Return,
    SourceUnit,
    StructDefinition,
    TupleExpression,
    UnaryOperation,
    UserDefinedTypeName,
    Mapping,
    Literal,
    VariableDeclaration,
    VariableDeclarationStatement,
)
from models.base_ast_models import NodeType

FILE_NAME = "contract.example.sol"
CONTRACT_NAME = "GalacticBank"


def compile_contract_from_file(filename: str, contract_name: str):
    with open(filename) as f:
        code = f.read()

    suggested_version = solcx.install.select_pragma_version(
        code, solcx.get_installable_solc_versions()
    )
    json_compiled = solcx.compile_source(code, solc_version=suggested_version)

    return json_compiled[f"<stdin>:{contract_name}"]["ast"]


def get_contract_variables(ast: SourceUnit) -> List[VariableDeclaration]:
    variables = []

    for node in ast.nodes:
        if node.node_type == NodeType.CONTRACT_DEFINITION:
            for contract_node in node.nodes:
                if contract_node.node_type == NodeType.VARIABLE_DECLARATION:
                    variables.append(contract_node)

    return variables


def get_contract_functions(ast: SourceUnit) -> List[FunctionDefinition]:
    functions = []

    for node in ast.nodes:
        if node.node_type == NodeType.CONTRACT_DEFINITION:
            for contract_node in node.nodes:
                if contract_node.node_type == NodeType.FUNCTION_DEFINITION:
                    functions.append(contract_node)

    return functions


def rename_variable_in_function(
    ast_node: FunctionDefinition, old_name: str, new_name: str
):
    for param in ast_node.parameters.parameters:
        if param.name == old_name:
            param.name = new_name

    for param in ast_node.return_parameters.parameters:
        if param.name == old_name:
            param.name = new_name

    def traverse_node(node):
        if isinstance(node, Identifier) and node.name == old_name:
            node.name = new_name

        elif isinstance(node, VariableDeclaration) and node.name == old_name:
            node.name = new_name

        elif isinstance(node, Block):
            for stmt in node.statements:
                traverse_node(stmt)

        elif isinstance(node, ExpressionStatement):
            traverse_node(node.expression)

        elif isinstance(node, Assignment):
            if node.left_hand_side:
                traverse_node(node.left_hand_side)
            if node.right_hand_side:
                traverse_node(node.right_hand_side)

        elif isinstance(node, BinaryOperation):
            traverse_node(node.left_expression)
            traverse_node(node.right_expression)

        elif isinstance(node, UnaryOperation):
            traverse_node(node.sub_expression)

        elif isinstance(node, FunctionCall):
            traverse_node(node.expression)
            for arg in node.arguments:
                traverse_node(arg)

        elif isinstance(node, MemberAccess):
            traverse_node(node.expression)
            if node.sub_expression:
                traverse_node(node.sub_expression)

        elif isinstance(node, IndexAccess):
            traverse_node(node.base_expression)
            traverse_node(node.index_expression)

        elif isinstance(node, TupleExpression):
            for comp in node.components:
                traverse_node(comp)

        elif isinstance(node, VariableDeclarationStatement):
            for decl in node.declarations:
                traverse_node(decl)
            if node.initial_value:
                traverse_node(node.initial_value)

        elif isinstance(node, Return):
            if node.expression:
                traverse_node(node.expression)

    traverse_node(ast_node.body)


def rename_variable_in_contract(ast: SourceUnit, old_name: str, new_name: str):
    for node in ast.nodes:
        if node.node_type == NodeType.CONTRACT_DEFINITION:
            for contract_node in node.nodes:
                if contract_node.node_type == NodeType.VARIABLE_DECLARATION:
                    if contract_node.name == old_name:
                        contract_node.name = new_name

                if contract_node.node_type == NodeType.FUNCTION_DEFINITION:
                    rename_variable_in_function(contract_node, old_name, new_name)

    return ast

def change_function_in_contract(
    ast: SourceUnit, new_function: FunctionDefinition
):
    for node in ast.nodes:
        if node.node_type == NodeType.CONTRACT_DEFINITION:
            for idx, contract_node in enumerate(node.nodes):
                if contract_node.node_type == NodeType.FUNCTION_DEFINITION:
                    if contract_node.kind == new_function.kind and contract_node.name == new_function.name:
                        node.nodes[idx] = new_function
                        return ast
    raise ValueError("Function not found in contract")
    

def check_function_in_contract(ast: SourceUnit, function_name: str):
    for node in ast.nodes:
        if node.node_type == NodeType.CONTRACT_DEFINITION:
            for contract_node in node.nodes:
                if contract_node.node_type == NodeType.FUNCTION_DEFINITION:
                    if contract_node.name == function_name:
                        return True
    return False

def check_storage_in_contract(ast: SourceUnit, storage_name: str):
    for node in ast.nodes:
        if node.node_type == NodeType.CONTRACT_DEFINITION:
            for contract_node in node.nodes:
                if contract_node.node_type == NodeType.VARIABLE_DECLARATION:
                    if contract_node.name == storage_name:
                        return True
    return False



def append_node_to_contract(
    ast: SourceUnit, node: Union[FunctionDefinition, VariableDeclaration]
):
    for ast_node in ast.nodes:
        if ast_node.node_type == NodeType.CONTRACT_DEFINITION:
            if node.node_type == NodeType.FUNCTION_DEFINITION:
                if node.kind == "constructor":
                    source_constructor = next(
                        func for func in ast_node.nodes if func.kind == "constructor"
                    )
                    if source_constructor:
                        source_constructor.body.statements += node.body.statements
                        continue

            else:
                last_var_declaration = next(
                    (
                        idx
                        for idx, contract_node in enumerate(reversed(ast_node.nodes))
                        if contract_node.node_type == NodeType.VARIABLE_DECLARATION
                    ),
                    None,
                )
                if last_var_declaration:
                    ast_node.nodes.insert(last_var_declaration, node)
                    continue

            ast_node.nodes.append(node)

    return ast


def main():
    solcx.install_solc()

    ast = compile_contract_from_file(FILE_NAME, CONTRACT_NAME)

    with open("contract_ast.json", "w+") as f:
        f.write(json.dumps(ast, indent=2))

    ast_obj_contract = SourceUnit(**ast)
    contract_source = parse_ast_to_solidity(ast_obj_contract)

    with open("restored.example.sol", "w+") as f:
        f.write(contract_source)


    ast_reentrancy = compile_contract_from_file("vulnerabilities/wallet.sol", "Wallet")

    with open("reentrancy_ast.json", "w+") as f:
        f.write(json.dumps(ast_reentrancy, indent=2))

    ast_obj_reentrancy = SourceUnit(
        **ast_reentrancy
    )

    contract_source = parse_ast_to_solidity(ast_obj_reentrancy)

    variables_of_source = get_contract_variables(ast_obj_contract)
    functions_of_source = get_contract_functions(ast_obj_reentrancy)

    variables_of_reentrancy = get_contract_variables(ast_obj_reentrancy)
    functions_of_reentrancy = get_contract_functions(ast_obj_reentrancy)

    
    for variable in variables_of_reentrancy:
        if not check_storage_in_contract(ast_obj_contract, variable.name):
            ast_obj_contract = append_node_to_contract(ast_obj_contract, variable)

    for function in functions_of_reentrancy:
        if check_function_in_contract(ast_obj_contract, function.name):
            change_function_in_contract(ast_obj_contract, function)
        else:
            ast_obj_contract = append_node_to_contract(ast_obj_contract, function) # TODO - max tries or logs

    # for variable in variables_of_reentrancy:
    #     if variable.name not in [var.name for var in variables_of_source]:
    #         ast_obj_contract = apppend_node_to_contract(ast_obj_contract, variable)
    #     else:
    #         old_name = variable.name
    #         variable.name = f"Test{variable.name}"  ## TODO - add a check for name uniqueness
    #         rename_variable_in_contract(ast_obj_reentrancy, old_name, variable.name)
    #         ast_obj_contract = apppend_node_to_contract(ast_obj_contract, variable)
            

    # for function in functions_of_reentrancy:
    #     if function.kind == "constructor":
    #         source_constructor = next(
    #             func for func in functions_of_source if func.kind == "constructor"
    #         )
    #         if source_constructor:
    #             source_constructor.body.statements += function.body.statements
    #         else:
    #             ast_obj_contract = apppend_node_to_contract(ast_obj_contract, function)
    #         continue
    #     if function in functions_of_source:
    #         function.name = (
    #             f"Test{function.name}"  ## TODO - add a check for name uniqueness
    #         )
    #     ast_obj_contract = apppend_node_to_contract(ast_obj_contract, function)

    contract_source = parse_ast_to_solidity(ast_obj_contract)

    suggested_version = solcx.install.select_pragma_version(
        contract_source, solcx.get_installable_solc_versions()
    )
    solcx.compile_source(contract_source, solc_version=suggested_version)

    with open("contract_with_vulnerability.sol", "w+") as f:
        f.write(contract_source)


if __name__ == "__main__":
    main()
