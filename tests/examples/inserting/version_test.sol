pragma solidity ^0.8.0;

contract VersionTestContract {
    string public constant VERSION = "1.0.0";
    address public owner;
    uint256 public createdAt;
    
    event VersionUpdated(string newVersion);
    
    constructor() {
        owner = msg.sender;
        createdAt = block.timestamp;
    }
    
    function getVersion() public pure returns (string memory) {
        return VERSION;
    }
    
    function updateVersion(string memory newVersion) public {
        require(msg.sender == owner, "Only owner can update version");
        emit VersionUpdated(newVersion);
    }
}
