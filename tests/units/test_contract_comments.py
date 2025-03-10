from os.path import isfile, join, dirname
from os import listdir
import unittest
import solcx
from solc_ast_parser.comments import insert_comments_into_ast
from solc_ast_parser.utils import (
    create_ast_with_standart_input,
)


CONTRACT_PATH = join(dirname(__file__), "..", "examples", "comments")


class AstToSourceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = [
            (f.split(".")[0], f)
            for f in listdir(CONTRACT_PATH)
            if isfile(join(CONTRACT_PATH, f) and f.endswith(".sol"))
        ]
        solcx.install_solc()

    def test_ast_to_source(self):
        for contract_name, contract_filename in self.contracts:
            with self.subTest(contract=contract_name):
                self._test_single_comment(contract_filename)

    def _test_single_comment(self, contract_filename):
        self.maxDiff = None

        with open(join(CONTRACT_PATH, contract_filename)) as f:
            source_code = f.read()
        ast = create_ast_with_standart_input(source_code, contract_filename)
        try:
            ast_with_comments = insert_comments_into_ast(source_code, ast)
        except Exception as ex:
            self.fail(
                f"Exception occurred while parsing {contract_filename} contract code: {ex}"
            )

        generated = ast_with_comments.parse()
        source = source_code.replace("\n", "").replace('"', "'")
        generated = generated.replace("\n", "")

        self.assertEqual(source, generated)


if __name__ == "__main__":
    unittest.main()
