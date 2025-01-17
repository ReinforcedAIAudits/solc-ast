pragma solidity ^0.8.0;

interface IExample {
    function getNumber() external view returns (uint256);
    function getText() external view returns (string memory);
}

contract BaseContract {
    uint256 baseNumber;
    string baseText;

    function setBaseData(uint256 _number, string memory _text) public {
        baseNumber = _number;
        baseText = _text;
    }

    function getBaseData() public view returns (uint256, string memory) {
        return (baseNumber, baseText);
    }
}

contract ExampleContract is BaseContract, IExample {
    address public owner;

    event DataUpdated(uint256 newNumber, string newText);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function getNumber() public view override returns (uint256) {
        return baseNumber;
    }

    function getText() public view override returns (string memory) {
        return baseText;
    }

    function updateData(uint256 newNumber, string memory newText) public onlyOwner {
        setBaseData(newNumber, newText);
        emit DataUpdated(newNumber, newText);
    }

    struct User {
        string name;
        uint256 age;
        bool isActive;
    }

    mapping(address => User) public users;

    function addUser(string memory name, uint256 age) public {
        users[msg.sender] = User(name, age, true);
    }

    function getUser() public view returns (string memory, uint256, bool) {
        User memory user = users[msg.sender];
        return (user.name, user.age, user.isActive);
    }

    function deactivateUser() public {
        users[msg.sender].isActive = false;
    }
}
