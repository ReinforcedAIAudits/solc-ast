import unittest

import solcx

from solc_ast_parser.models.base_ast_models import NodeType
from solc_ast_parser.models.ast_models import (
    PragmaDirective,
    UsingForDirective,
    IdentifierPath,
)
from solc_ast_parser.utils import (
    create_ast_from_source,
    insert_node,
)


class VersionInsertionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        solcx.install_solc()

    def test_pragma_version_insertion(self):
        source_code = """
contract SimpleContract {
    uint256 public value;
    
    function setValue(uint256 _value) public {
        value = _value;
    }
}
"""

        ast = create_ast_from_source(source_code)
        pragma_node = PragmaDirective(
            id=999999,
            src="0:25:0",
            nodeType=NodeType.PRAGMA_DIRECTIVE,
            literals=["solidity", "^0.8.30"],
        )

        success = insert_node(ast, ast.nodes[0].id, pragma_node, position="before")

        self.assertTrue(success, "Failed to insert pragma directive")

        generated = ast.to_solidity()
        self.assertIn("pragma solidity ^0.8.30;", generated)

    def test_multiple_pragma_insertion(self):
        source_code = """
contract MultiPragmaContract {
    uint256 public counter;
}
"""

        ast = create_ast_from_source(source_code)
        solidity_pragma = PragmaDirective(
            id=999998,
            src="0:25:0",
            nodeType=NodeType.PRAGMA_DIRECTIVE,
            literals=["solidity", "^0.8.19"],
        )

        experimental_pragma = PragmaDirective(
            id=999997,
            src="26:35:0",
            nodeType=NodeType.PRAGMA_DIRECTIVE,
            literals=["experimental", "ABIEncoderV2"],
        )

        insert_node(ast, ast.nodes[0].id, solidity_pragma, position="before")
        insert_node(ast, ast.nodes[0].id, experimental_pragma, position="before")

        generated = ast.to_solidity()

        self.assertIn("pragma solidity ^0.8.19;", generated)
        self.assertIn("pragma experimental ABIEncoderV2;", generated)

    def test_version_insertion_with_existing_pragma(self):
        source_code = """pragma solidity ^0.8.0;

contract ExistingPragmaContract {
    string public name;
}
"""

        ast = create_ast_from_source(source_code)

        new_pragma = PragmaDirective(
            id=999996,
            src="0:25:0",
            nodeType=NodeType.PRAGMA_DIRECTIVE,
            literals=["solidity", "^0.8.20"],
        )

        contract_node = None
        for node in ast.nodes:
            if node.node_type == NodeType.CONTRACT_DEFINITION:
                contract_node = node
                break

        self.assertIsNotNone(contract_node, "Contract node not found")

        success = insert_node(ast, contract_node.id, new_pragma, position="before")
        self.assertTrue(success, "Failed to insert new pragma directive")

        generated = ast.to_solidity()

        self.assertIn("pragma solidity ^0.8.0;", generated)
        self.assertIn("pragma solidity ^0.8.20;", generated)

    def test_version_metadata_insertion(self):
        source_code = """
contract VersionedContract {
    uint256 public data;
    
    function setData(uint256 _data) public {
        data = _data;
    }
}
"""

        ast = create_ast_from_source(source_code)

        contract_node = None
        for node in ast.nodes:
            if node.node_type == NodeType.CONTRACT_DEFINITION:
                contract_node = node
                break

        self.assertIsNotNone(contract_node, "Contract node not found")

        contract_node.documentation = "Contract version: 1.0.0"

        generated = ast.to_solidity()
        self.assertIn("/// Contract version: 1.0.0", generated)

    def test_solc_version_compatibility_check(self):
        test_versions = ["^0.8.0", "^0.8.19", ">=0.8.0<0.9.0"]

        for version in test_versions:
            with self.subTest(version=version):
                source_code = f"""pragma solidity {version};

contract VersionTest {{
    uint256 public value = 42;
}}
"""
                try:
                    ast = create_ast_from_source(source_code)
                    generated = ast.to_solidity()
                    self.assertIn(f"pragma solidity {version};", generated)
                except Exception as e:
                    self.fail(f"Failed to process version {version}: {e}")

    def test_using_directive_insertion(self):
        source_code = """
contract MathContract {
    uint256 public value;
    
    function add(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b;
    }
}
"""

        ast = create_ast_from_source(source_code)

        contract_node = None
        for node in ast.nodes:
            if node.node_type == NodeType.CONTRACT_DEFINITION:
                contract_node = node
                break

        self.assertIsNotNone(contract_node, "Contract node not found")

        using_directive = UsingForDirective(
            id=999995,
            src="0:30:0",
            nodeType=NodeType.USING_FOR_DIRECTIVE,
            libraryName=IdentifierPath(
                id=999994,
                src="6:8:0",
                nodeType=NodeType.IDENTIFIER_PATH,
                name="SafeMath",
                nameLocations=["6:8:0"],
            ),
            typeName=None,
        )

        success = insert_node(
            ast, contract_node.id, using_directive, position="child_first"
        )

        self.assertTrue(success, "Failed to insert using directive")

        generated = ast.to_solidity()
        self.assertIn("using SafeMath for", generated)
        self.assertIn("contract MathContract", generated)

        lines = generated.split("\n")
        using_line_idx = None
        value_line_idx = None

        for i, line in enumerate(lines):
            if "using SafeMath for" in line:
                using_line_idx = i
            if "uint256 public value" in line:
                value_line_idx = i

        self.assertIsNotNone(
            using_line_idx, "Using directive not found in generated code"
        )
        self.assertIsNotNone(
            value_line_idx, "Value declaration not found in generated code"
        )
        self.assertLess(
            using_line_idx,
            value_line_idx,
            "Using directive should appear before value declaration",
        )


if __name__ == "__main__":
    unittest.main()
