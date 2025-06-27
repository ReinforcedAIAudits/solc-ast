pragma solidity ^0.8.0;

contract EnhancedContract {
    uint256 public number;
    string public text;
    address public owner;
    mapping(address => uint256) public balances;
    bool public isActive;
    address[] public users;

    event NumberUpdated(uint256 newNumber);
    event TextUpdated(string newText);
    event BalanceUpdated(address indexed user, uint256 newBalance);
    event ContractStatusChanged(bool isActive);
    event UserAdded(address indexed user);

    constructor(string memory initialText) {
        owner = msg.sender;
        text = initialText;
        isActive = true;
    }

    function updateNumber(uint256 newNumber) public {
        require(isActive, "Contract is not active");
        number = newNumber;
        emit NumberUpdated(newNumber);
    }

    function updateText(string memory newText) public {
        require(msg.sender == owner, "Only owner can update text");
        text = newText;
        emit TextUpdated(newText);
    }

    function deposit() public payable {
        require(isActive, "Contract is not active");
        balances[msg.sender] += msg.value;
        users.push(msg.sender);
        emit BalanceUpdated(msg.sender, balances[msg.sender]);
        emit UserAdded(msg.sender);
    }

    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }

    function toggleActiveStatus() public {
        require(msg.sender == owner, "Only owner can change status");
        isActive = !isActive;
        emit ContractStatusChanged(isActive);
    }

    function getContractInfo() public view returns (uint256, string memory, bool) {
        return (number, text, isActive);
    }

    function getAllUsers() public view returns (address[] memory) {
        return users;
    }

    function getAllBalances() public view returns (uint256[] memory) {
        uint256[] memory allBalances = new uint256[](users.length);
        for (uint256 i = 0; i < users.length; i++) {
            allBalances[i] = balances[users[i]];
        }
        return allBalances;
    }

    function isUser(address user) public view returns (bool) {
        for (uint256 i = 0; i < users.length; i++) {
            if (users[i] == user) {
                return true;
            }
        }
        return false;
    }
}
