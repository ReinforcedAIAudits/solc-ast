pragma solidity ^0.8.0;

contract AddressManager {

    address[] private addresses;

    event AddressAdded(address indexed account);

    function isContract(address account) internal view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(account) }
        return size > 0;
    }

    function addAddress(address account) external {
        require(account != address(0), "Incorrect address");
        require(!isContract(account), "Address is a contract");

        addresses.push(account);
        emit AddressAdded(account);
    }

    function getAddressCount() external view returns (uint256) {
        return addresses.length;
    }

    function getAddress(uint256 index) external view returns (address) {
        require(index < addresses.length, "Index out of bounds");
        return addresses[index];
    }

    function checkIfContract(address account) external view returns (bool) {
        return isContract(account);
    }
}
