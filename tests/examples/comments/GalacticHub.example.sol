// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GalacticHub {
    address private owner; // Owner of the contract
    mapping(address => uint256) public userBalances;
    // Mapping to store the allowance given by one user to another
    uint256 public totalSupply;
    // Total supply of the contract
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public feePercentage;

    // Constructor
    constructor() {
        owner = msg.sender;
        totalSupply = 0; // Initialize the total supply to zero
        feePercentage = 5;
    }

    // Deposit funds into the contract
    function deposit() public payable {
        userBalances[msg.sender] += msg.value; // Increase the user balance
        totalSupply += msg.value;
    }

    /* Withdraw funds from the contract
    * @param amount amount to be withdrawn
    */
    function withdraw(uint256 amount) public {
        require(userBalances[msg.sender] >= amount, "Insufficient balance"); // Check if the user has enough balance
        userBalances[msg.sender] -= amount;
        totalSupply -= amount; // Decrease the total supply of the contract
        // Transfer the amount to the user
        payable(msg.sender).transfer(amount);
    }

    // Transfer funds from one user to another
    function transfer(address recipient, uint256 amount) public {
        require(userBalances[msg.sender] >= amount, "Insufficient balance"); // Check if the user has enough balance
        userBalances[msg.sender] -= amount;
        userBalances[recipient] += amount; // Increase the recipient balance
    }

    // Set the fee percentage
    function setFeePercentage(uint256 newFee) public {
        // Only the owner can set the fee percentage
        require(msg.sender == owner, "Only the owner can set the fee percentage");
        feePercentage = newFee;
    }
}