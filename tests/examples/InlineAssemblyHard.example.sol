pragma solidity ^0.8.0;

contract ExampleContract {
    uint256 public number;
    string public text;
    address public owner;
    mapping(address => uint256) public balances;
    uint256[] public values;

    constructor() {
        owner = msg.sender;
    }

    function setNumber(uint256 _number) public {
        number = _number;
    }

    function getNumber() public view returns (uint256) {
        return number;
    }

    function addValue(uint256 _value) public {
        values.push(_value);
    }

    function getBalance(address _address) public view returns (uint256) {
        return balances[_address];
    }

    function updateBalance(address _address, uint256 _amount) public {
        balances[_address] += _amount;
    }

    function exampleAssembly(uint256 _input) public pure returns (uint256) {
        uint256 result;
        assembly {
            result := _input
            if gt(result, 10) {
                result := mul(result, 2)
            }

            if eq(result, 10) {
                result := add(result, 5)
            }

            for { let i := 0 } lt(i, 5) { i := add(i, 1) } {
                result := add(result, i)
            }

        }
        return result;
    }

}
