import json
from os.path import isfile, join, dirname
from os import listdir
import unittest
import solcx

from solc_ast_parser.models.ast_models import SourceUnit

CONTRACT_PATH = join(dirname(__file__), "..", "examples")

class ContractToAstTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = [
            (f.split('.')[0], f) for f in listdir(CONTRACT_PATH) if isfile(join(CONTRACT_PATH, f) and f.endswith(".sol"))
        ]
        solcx.install_solc()

    def test_contracts_to_ast(self):
        for contract_name, contract_filename in self.contracts:
            with self.subTest(contract=contract_name):
                self._test_single_contract(contract_filename)

    def _test_single_contract(self, contract_filename):
        with open(join(CONTRACT_PATH, contract_filename)) as f:
            source_code = f.read()
        suggested_version = solcx.install.select_pragma_version(
            source_code, solcx.get_installable_solc_versions()
        )
        solc_output = solcx.compile_source(source_code, solc_version=suggested_version)
        try:
            contract_name = list(solc_output.keys())[0]
            ast = SourceUnit(**solc_output[contract_name]["ast"])
        except Exception as ex:
            with open(join(CONTRACT_PATH, f"{contract_name}.errors.txt"), "w") as f:
                f.write(str(ex))
            with open(join(CONTRACT_PATH, f"{contract_name}.ast.json"), "w") as f:
                f.write(json.dumps(solc_output[contract_name]["ast"], indent=2))
            self.fail(f"Exception occurred while parsing {contract_name} contract code: {ex}")

if __name__ == "__main__":
    unittest.main()
