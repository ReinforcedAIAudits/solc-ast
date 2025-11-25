# SOLC-AST Parser

A Python library for parsing Solidity smart contracts into Abstract Syntax Trees (AST) and converting them back to source code. This library provides powerful tools for analyzing, modifying, and transforming Solidity contracts programmatically.

## Features

- 🔄 **Bidirectional conversion**: Solidity source ↔ AST
- 🔍 **AST traversal and analysis**: Find nodes, analyze structure
- ✏️ **Code modification**: Insert, remove, replace, and reorder nodes
- 📝 **Comment preservation**: Maintain comments during transformations
- 🔧 **Flexible configuration**: Customize output formatting

## Installation

```bash
pip install solc-ast-parser
```

## Quick Start

### Basic Usage

```python
from solc_ast_parser.utils import create_ast_from_source
from solc_ast_parser.models.base_ast_models import NodeType

# Parse Solidity source code
contract_source = """
pragma solidity ^0.8.0;

contract SimpleContract {
    uint256 public value;
    
    function setValue(uint256 _value) public {
        value = _value;
    }
}
"""

# Create AST
ast = create_ast_from_source(contract_source)

# Convert back to source
generated_code = ast.to_solidity()
print(generated_code)
```

### Finding Nodes

```python
from solc_ast_parser.utils import find_node_with_properties
from solc_ast_parser.models.base_ast_models import NodeType

# Find all function definitions
functions = find_node_with_properties(
    ast, 
    node_type=NodeType.FUNCTION_DEFINITION
)

# Find specific function by name
set_value_function = find_node_with_properties(
    ast, 
    node_type=NodeType.FUNCTION_DEFINITION,
    name="setValue"
)

# Find all variable declarations
variables = find_node_with_properties(
    ast,
    node_type=NodeType.VARIABLE_DECLARATION
)
```

### Modifying Contracts

#### Adding Pragma Directives

```python
from solc_ast_parser.models.ast_models import PragmaDirective
from solc_ast_parser.models.base_ast_models import NodeType
from solc_ast_parser.utils import insert_node

# Create a new pragma directive
pragma_node = PragmaDirective(
    id=999999, # this field is no matter
    src="0:25:0", # this field is no matter
    nodeType=NodeType.PRAGMA_DIRECTIVE,
    literals=["solidity", "^0.8.30"],
)

# Insert before the first contract
success = insert_node(
    ast, 
    ast.nodes[0].id, 
    pragma_node, 
    position="before"
)
```

#### Adding Using Directives

```python
from solc_ast_parser.models.ast_models import UsingForDirective, IdentifierPath

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

# Insert as first child of contract
success = insert_node(
    ast, 
    contract_node.id, 
    using_directive, 
    position="child_first"
)
```

### Node Manipulation

#### Replacing Nodes

```python
from solc_ast_parser.utils import replace_node, replace_node_to_multiple

# Replace a single node
success = replace_node(ast, target_node_id, new_node)

# Replace a node with multiple nodes
success = replace_node_to_multiple(ast, target_node_id, [node1, node2, node3])
```

#### Removing Nodes

```python
from solc_ast_parser.utils import remove_node

# Remove a node by ID
success = remove_node(ast, target_node_id)
```

#### Updating Node Fields

```python
from solc_ast_parser.utils import update_node_fields

# Update all function names to add "Updated" suffix
functions = find_node_with_properties(ast, node_type=NodeType.FUNCTION_DEFINITION)

for function in functions:
    update_node_fields(
        ast, 
        {"node_type": NodeType.FUNCTION_DEFINITION, "name": function.name}, 
        {"name": f"{function.name}Updated"}
    )
```

### AST Traversal

```python
from solc_ast_parser.utils import traverse_ast

def visitor(node, parent):
    if hasattr(node, 'node_type'):
        print(f"Node: {node.node_type}")
        if hasattr(node, 'name'):
            print(f"  Name: {node.name}")

# Traverse the entire AST
traverse_ast(ast, visitor)
```

### Contract Reordering

```python
from solc_ast_parser.utils import (
    reorder_nodes_by_types, 
    group_nodes_by_type,
    shuffle_functions_and_storages
)

# Reorder nodes by type
reorder_nodes_by_types(
    ast, 
    [NodeType.STRUCT_DEFINITION, NodeType.VARIABLE_DECLARATION, NodeType.FUNCTION_DEFINITION]
)

# Group nodes by their types
group_nodes_by_type(ast, target_contract_name="MyContract")

# Randomly shuffle functions and storage variables
shuffle_functions_and_storages(ast, seed=42)
```

### Working with Comments

```python
from solc_ast_parser.utils import create_ast_with_standart_input
from solc_ast_parser.comments import insert_comments_into_ast

contract_with_comments = """
pragma solidity ^0.8.0;

/// @title Simple Contract
contract SimpleContract {
    uint256 public value; // Storage variable
    
    /// @notice Set a new value
    function setValue(uint256 _value) public {
        value = _value; // Update storage
    }
}
"""

# Parse with comments
ast = create_ast_with_standart_input(contract_with_comments)
ast_with_comments = insert_comments_into_ast(contract_with_comments, ast)

# Generate code preserving comments
generated = ast_with_comments.to_solidity()
```

### Quote Preferences

```python
from solc_ast_parser.models.base_ast_models import SolidityConfig, QuotePreference

# Use single quotes
config = SolidityConfig(quote_preference=QuotePreference.SINGLE)
single_quote_output = ast.to_solidity(config=config)

# Use double quotes (default)
double_quote_output = ast.to_solidity()
```

### Advanced Example: Contract Analysis

```python
from solc_ast_parser.models.base_ast_models import NodeType
from solc_ast_parser.utils import find_node_with_properties, traverse_ast

def analyze_contract_complexity(ast):
    """Analyze contract complexity metrics."""
    
    # Count different node types
    functions = find_node_with_properties(ast, node_type=NodeType.FUNCTION_DEFINITION)
    modifiers = find_node_with_properties(ast, node_type=NodeType.MODIFIER_DEFINITION)
    events = find_node_with_properties(ast, node_type=NodeType.EVENT_DEFINITION)
    state_vars = find_node_with_properties(ast, node_type=NodeType.VARIABLE_DECLARATION)
    
    # Find external/public functions
    public_functions = [f for f in functions if f.visibility in ['public', 'external']]
    
    # Count loops
    loops = []
    traverse_ast(ast, lambda n, p: loops.append(n) if hasattr(n, 'node_type') and 
                 n.node_type in [NodeType.FOR_STATEMENT, NodeType.WHILE_STATEMENT] else None)
    
    return {
        'functions': len(functions),
        'public_functions': len(public_functions),
        'modifiers': len(modifiers),
        'events': len(events),
        'state_variables': len(state_vars),
        'loops': len(loops)
    }

# Usage
complexity = analyze_contract_complexity(ast)
print(f"Contract has {complexity['functions']} functions, "
      f"{complexity['public_functions']} public, "
      f"{complexity['loops']} loops")
```

## API Reference

### Core Functions

- `create_ast_from_source(source: str) -> SourceUnit`: Parse Solidity source to AST
- `create_ast_with_standart_input(source: str, filename: str) -> SourceUnit`: Parse with standard input
- `find_node_with_properties(ast, **kwargs) -> List[ASTNode]`: Find nodes matching criteria
- `traverse_ast(node, visitor, parent=None)`: Traverse AST with visitor function
- `insert_node(ast, target_id, new_node, position)`: Insert new node
- `replace_node(ast, target_id, replacement)`: Replace existing node
- `remove_node(ast, target_id)`: Remove node from AST
- `update_node_fields(ast, target_fields, new_values)`: Update node properties

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.