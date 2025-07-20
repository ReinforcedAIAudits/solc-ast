pragma solidity ^0.8.30;

contract FundsManager {
    address public owner;
    uint256 public totalWithdrawn;
    mapping(address => uint256) public withdrawnByAddress;
    event TransferSent(address indexed from, address indexed to, uint256 amount);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event FundsDeposited(address indexed from, uint256 amount);
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }
    constructor() {
        owner = msg.sender;
        totalWithdrawn = 0;
    }

    function pullFunds(uint256 amount, address payable to) public onlyOwner {
        require(address(this).balance >= amount, "Insufficient funds");
        to.transfer(amount);
        emit TransferSent(msg.sender, to, amount);
    }

    function depositFunds() public payable {
        require(msg.value > 0, "Must send some ether");
        emit FundsDeposited(msg.sender, msg.value);
    }

    function getContractBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner cannot be zero address");
        address previousOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(previousOwner, newOwner);
    }

    receive() external payable {
        emit FundsDeposited(msg.sender, msg.value);
    }

}

