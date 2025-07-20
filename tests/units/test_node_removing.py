from os.path import isfile, join, dirname
import unittest
from os import listdir

import solcx

from solc_ast_parser.models.base_ast_models import NodeType
from solc_ast_parser.utils import (
    compile_contract_from_source,
    create_ast_from_source,
    find_node_with_properties,
    remove_node,
    replace_node,
    replace_node_to_multiple,
)

BASE_CONTRACT_PATH = join(dirname(__file__), "..", "examples", "removing", "base")
EXPECTED_CONTRACT_PATH = join(
    dirname(__file__), "..", "examples", "removing", "expected"
)


class ContractToAstTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.base_contracts = [
            (f.split(".")[0], f)
            for f in listdir(BASE_CONTRACT_PATH)
            if isfile(join(BASE_CONTRACT_PATH, f) and f.endswith(".sol"))
        ]

        cls.expected_contracts = [
            (f.split(".")[0], f)
            for f in listdir(EXPECTED_CONTRACT_PATH)
            if isfile(join(EXPECTED_CONTRACT_PATH, f) and f.endswith(".sol"))
        ]

        solcx.install_solc()

    def test_removing_nodes(self):
        for base_contract_name, base_contract_filename in self.base_contracts:
            with self.subTest(base_contract=base_contract_name):
                self._test_single_contract(base_contract_filename, base_contract_name)

    def _test_single_contract(self, base_contract_filename, base_contract_name):
        with open(join(BASE_CONTRACT_PATH, base_contract_filename)) as f:
            base_source_code = f.read()

        with open(join(EXPECTED_CONTRACT_PATH, f"{base_contract_name}.sol")) as f:
            expected_source_code = f.read()

        ast = create_ast_from_source(base_source_code)

        intialize_definition = find_node_with_properties(
            ast,
            node_type=NodeType.FUNCTION_DEFINITION,
            name="initialize",
        )

        self.assertEqual(
            len(intialize_definition),
            1,
            f"Expected one 'initialize' function definition in {base_contract_name}",
        )

        result = remove_node(
            ast,
            intialize_definition[0].id,
        )

        self.assertTrue(
            result,
            f"Failed to replace 'initialize' function call in {base_contract_name}",
        )

        generated = ast.to_solidity()

        source = expected_source_code.replace("\n", "")
        generated = generated.replace("\n", "")
        self.assertEqual(source, generated)
