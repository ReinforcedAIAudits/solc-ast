import json
from os.path import isfile, join, dirname
from os import listdir
import unittest
import solcx
from solc_ast_parser.models.ast_models import SourceUnit
from solc_ast_parser.models.base_ast_models import QuotePreference, SolidityConfig


CONTRACT_PATH = join(dirname(__file__), "..", "examples")


class AstToSourceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = [
            (f.split(".")[0], f)
            for f in listdir(CONTRACT_PATH)
            if isfile(join(CONTRACT_PATH, f) and f.endswith(".sol"))
        ]
        solcx.install_solc()

    def test_ast_to_source_double_quote(self):
        for contract_name, contract_filename in self.contracts:
            with self.subTest(contract=contract_name):
                self._test_default_config(contract_filename)


    def test_ast_to_source_single_quote(self):
        for contract_name, contract_filename in self.contracts:
            with self.subTest(contract=contract_name):
                self._test_single_quote_config(contract_filename)

    def _test_default_config(self, contract_filename):
        self.maxDiff = None

        with open(join(CONTRACT_PATH, contract_filename)) as f:
            source_code = f.read()
        suggested_version = solcx.install.select_pragma_version(
            source_code, solcx.get_installable_solc_versions()
        )
        solc_output = solcx.compile_source(source_code, solc_version=suggested_version)
        contract_name = list(solc_output.keys())[0]
        ast = SourceUnit(**solc_output[contract_name]["ast"])
        try:
            generated = ast.to_solidity()
        except Exception as ex:
            self.fail(
                f"Exception occurred while parsing {contract_name} contract code: {ex}"
            )

        source = source_code.replace("\n", "").replace("\'", '"')
        generated = generated.replace("\n", "")

        print(f"Generated code: {generated}")

        self.assertEqual(source, generated)

    def _test_single_quote_config(self, contract_filename):
        self.maxDiff = None

        with open(join(CONTRACT_PATH, contract_filename)) as f:
            source_code = f.read()
        suggested_version = solcx.install.select_pragma_version(
            source_code, solcx.get_installable_solc_versions()
        )
        solc_output = solcx.compile_source(source_code, solc_version=suggested_version)
        contract_name = list(solc_output.keys())[0]
        ast = SourceUnit(**solc_output[contract_name]["ast"])
        try:
            generated = ast.to_solidity(config=SolidityConfig(quote_preference=QuotePreference.SINGLE))
        except Exception as ex:
            self.fail(
                f"Exception occurred while parsing {contract_name} contract code: {ex}"
            )

        source = source_code.replace("\n", "").replace('"', "'")
        generated = generated.replace("\n", "")

        print(f"Generated code: {generated}")

        self.assertEqual(source, generated)


if __name__ == "__main__":
    unittest.main()
