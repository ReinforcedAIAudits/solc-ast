import json
import solcx

from solc_ast_parser.models.ast_models import SourceUnit


def create_standart_solidity_input(contract_content: str, contract_name: str) -> dict:
    return {
        "language": "Solidity",
        "sources": {
            contract_name: {
                "content": contract_content,
            },
        },
        "settings": {
            "stopAfter": "parsing",
            "outputSelection": {"*": {"": ["ast"]}},
        },
    }


def compile_contract_from_source(source: str):
    suggested_version = solcx.install.select_pragma_version(
        source, solcx.get_installable_solc_versions()
    )
    json_compiled = solcx.compile_source(source, solc_version=suggested_version)
    return json_compiled[list(json_compiled.keys())[0]]["ast"]


def compile_contract_with_standart_input(
    source: str, contract_file_name: str = "example.sol"
):
    suggested_version = solcx.install.select_pragma_version(
        source, solcx.get_installable_solc_versions()
    )
    json_compiled = solcx.compile_standard(
        create_standart_solidity_input(source, contract_file_name),
        solc_version=suggested_version,
    )["sources"]
    return json_compiled[list(json_compiled.keys())[0]]["ast"]


def create_ast_from_source(source: str) -> SourceUnit:
    ast = compile_contract_from_source(source)
    return SourceUnit(**ast)


def create_ast_with_standart_input(
    source: str, contract_file_name: str = "example.sol"
) -> SourceUnit:
    ast = compile_contract_with_standart_input(source, contract_file_name)
    return SourceUnit(**ast)
