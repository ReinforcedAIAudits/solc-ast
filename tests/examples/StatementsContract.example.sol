pragma solidity ^0.8.0;

contract StatementsContract {
    uint256 public number;
    string public text;
    address public owner;

    event NumberUpdated(uint256 newNumber);
    event TextUpdated(string newText);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    constructor(uint256 initialNumber, string memory initialText) {
        number = initialNumber;
        text = initialText;
        owner = msg.sender;
    }

    function updateNumber(uint256 newNumber) public onlyOwner {
        number = newNumber;
        emit NumberUpdated(newNumber);
    }

    function updateText(string memory newText) public onlyOwner {
        text = newText;
        emit TextUpdated(newText);
    }

    function getCurrentState() public view returns (uint256, string memory) {
        return (number, text);
    }

    receive() external payable {}

    function withdraw() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    struct User {
        string name;
        uint256 age;
    }

    mapping(address => User) public users;

    function addUser(string memory name, uint256 age) public {
        users[msg.sender] = User(name, age);
    }

    function getUser() public view returns (string memory, uint256) {
        User memory user = users[msg.sender];
        return (user.name, user.age);
    }
}
