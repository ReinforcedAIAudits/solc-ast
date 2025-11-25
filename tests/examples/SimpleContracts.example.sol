pragma solidity ^0.8.0;

uint256 constant WAD = 1e18;
contract Relayer {
    mapping(bytes => bool) executed;
    address target;
    function forward(bytes memory _data) public {
        require(executed[_data] == false, "Replay protection");
        executed[_data] = true;
        target.call(abi.encodeWithSignature("execute(bytes)", _data));
    }
}

contract Wallet {
    mapping(address => uint) userBalance;
    function getBalance(address u) public returns (uint) {
        return userBalance[u];
    }

    function addToBalance() public payable {
        userBalance[msg.sender] += msg.value;
    }

    function withdrawBalance() public {
        (bool success, ) = msg.sender.call{value: userBalance[msg.sender]}("");
        if (!success) {
            revert();
        }
        userBalance[msg.sender] = 0;
    }
}


interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
}

contract Bridge {
    address public owner;
    event Deposit(address _token, uint256 _amount);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    function changeOwner(address _newOwner) public onlyOwner {
        require(_newOwner != address(0), "New owner cannot be zero address");
        owner = _newOwner;
    }

    function deposit(address _token, uint256 _amount) public {
        require(_token != address(0), "Token address cannot be zero");
        require(_amount > 0, "Amount must be greater than zero");
        require(IERC20(_token).transferFrom(msg.sender, address(this), _amount), "Transfer failed");
        emit Deposit(_token, _amount);
    }

    function withdraw(address _token, uint256 _amount) public onlyOwner {
        require(_token != address(0), "Token address cannot be zero");
        require(_amount > 0, "Amount must be greater than zero");
        require(IERC20(_token).transfer(msg.sender, _amount), "Transfer failed");
    }
}