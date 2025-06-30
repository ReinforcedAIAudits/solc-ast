pragma solidity ^0.8.30;

contract MultiSignatureWallet {
    struct PublicKey {
        uint256 x;
        uint256 y;
    }

    uint256 constant MAX_OWNERS = 10;
    PublicKey[MAX_OWNERS] public owners;
    uint256 public ownerCount;
    uint256 public requiredSignatures;
    uint256 public transactionCount;

    mapping(uint256 => Transaction) public transactions;
    mapping(uint256 => mapping(uint256 => bool)) public confirmations;

    struct Transaction {
        address destination;
        uint256 value;
        bytes data;
        bool executed;
    }

    event TransactionSubmitted(uint256 indexed transactionId);
    event TransactionConfirmed(uint256 indexed transactionId, uint256 ownerIndex);
    event TransactionExecuted(uint256 indexed transactionId);

    constructor(PublicKey[] memory _initialOwners, uint256 _requiredSignatures) {
        require(_initialOwners.length <= MAX_OWNERS, "Too many initial owners");
        require(_requiredSignatures <= _initialOwners.length, "Invalid signature requirement");
        require(_requiredSignatures > 0, "At least one signature required");

        for (uint256 i = 0; i < _initialOwners.length; i++) {
            require(!hasKey(owners, _initialOwners[i], ownerCount), "Duplicate owner");
            owners[ownerCount] = _initialOwners[i];
            ownerCount++;
        }

        requiredSignatures = _requiredSignatures;
    }

    function indexOf(PublicKey[MAX_OWNERS] memory keys, PublicKey memory owner, uint256 length) internal pure returns (uint256) {
        for (uint256 i = 0; i < length; ++i) {
            if (keys[i].x == owner.x && keys[i].y == owner.y) {
                return i;
            }
        }
        return type(uint256).max;
    }

    function hasKey(PublicKey[MAX_OWNERS] memory keys, PublicKey memory owner, uint256 length) internal pure returns (bool) {
        for (uint256 i = 0; i < length; ++i) {
            if (keys[i].x == owner.x && keys[i].y == owner.y) {
                return true;
            }
        }
        return false;
    }

    function submitTransaction(address _destination, uint256 _value, bytes calldata _data) external returns (uint256) {
        uint256 transactionId = transactionCount;
        transactions[transactionId] = Transaction({destination: _destination, value: _value, data: _data, executed: false});

        transactionCount++;
        emit TransactionSubmitted(transactionId);
        return transactionId;
    }

    function confirmTransaction(uint256 _transactionId, PublicKey memory _ownerKey) external {
        require(_transactionId < transactionCount, "Invalid transaction ID");
        require(!transactions[_transactionId].executed, "Transaction already executed");

        uint256 ownerIndex = indexOf(owners, _ownerKey, ownerCount);
        require(ownerIndex != type(uint256).max, "Not an owner");
        require(!confirmations[_transactionId][ownerIndex], "Transaction already confirmed");

        confirmations[_transactionId][ownerIndex] = true;
        emit TransactionConfirmed(_transactionId, ownerIndex);

        executeTransactionIfConfirmed(_transactionId);
    }

    function executeTransactionIfConfirmed(uint256 _transactionId) internal {
        if (isConfirmed(_transactionId)) {
            Transaction storage transaction = transactions[_transactionId];
            transaction.executed = true;

            (bool success, ) = transaction.destination.call{value: transaction.value}(transaction.data);
            require(success, "Transaction execution failed");

            emit TransactionExecuted(_transactionId);
        }
    }

    function isConfirmed(uint256 _transactionId) public view returns (bool) {
        uint256 confirmationCount = 0;

        for (uint256 i = 0; i < ownerCount; i++) {
            if (confirmations[_transactionId][i]) {
                confirmationCount++;
            }
            if (confirmationCount >= requiredSignatures) {
                return true;
            }
        }

        return false;
    }

    receive() external payable {}
}