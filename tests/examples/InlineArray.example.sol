pragma solidity ^0.8.30;

library SafeMath {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, 'SafeMath: addition overflow');
        return c;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a, 'SafeMath: subtraction overflow');
        return a - b;
    }

    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        if (a == 0) {
            return 0;
        }
        uint256 c = a * b;
        require(c / a == b, 'SafeMath: multiplication overflow');
        return c;
    }

    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b > 0, 'SafeMath: division by zero');
        uint256 c = a / b;
        return c;
    }

}

interface INoteAdapter {
    function isRepaid(uint256 maintenanceId) external view returns (bool);

}

library PRBMathUD60x18 {
    function mul(uint256 x, uint256 y) internal pure returns (uint256) {
        return (x * y) / 1e18;
    }

}

enum LoanStatus {
    Inactive,
    Active,
    Complete,
    Defaulted
}
struct Loan {
    LoanStatus status;
    uint256 seniorTrancheReturn;
    uint256 repayment;
}
contract LoanManager {
    using SafeMath for uint256;
    mapping(address => mapping(uint256 => Loan)) _loans;
    mapping(address => INoteAdapter) _noteAdapters;
    mapping(address => uint256) balances;

    uint256 _adminFeeRate;
    address _treasury;
    address _owner;
    event LoanRepaid(address indexed lienToken, uint256 indexed maintenanceId, uint256 interestAllocation, uint256[2] trancheReturns);
    error InvalidLoanStatus();
    error UnsupportedNoteToken();
    error LoanNotRepaid();
    error Unauthorized();
    constructor(address treasury, uint256 adminFeeRate) {
        _treasury = treasury;
        _adminFeeRate = adminFeeRate;
        _owner = msg.sender;
        balances[_treasury] = 0;
    }

    function loanRepaidEvent(address lienToken, uint256 maintenanceId) public {
        Loan storage financingLoan = _loans[lienToken][maintenanceId];
        if (financingLoan.status != LoanStatus.Active) {
            revert InvalidLoanStatus();
        }
        INoteAdapter noteContract = _getNoteAdapter(lienToken);
        if (address(noteContract) == address(0)) {
            revert UnsupportedNoteToken();
        }
        if (!noteContract.isRepaid(maintenanceId)) {
            revert LoanNotRepaid();
        }
        financingLoan.status = LoanStatus.Complete;
        uint256 primaryReturnDisclosure = financingLoan.seniorTrancheReturn;
        uint256 interestAllocation = PRBMathUD60x18.mul(_adminFeeRate, primaryReturnDisclosure);
        uint256 juniorFraction = financingLoan.repayment - primaryReturnDisclosure - interestAllocation;
        _processProceeds(financingLoan.repayment);
        emit LoanRepaid(lienToken, maintenanceId, interestAllocation, [primaryReturnDisclosure, juniorFraction]);
    }

    function _getNoteAdapter(address lienToken) internal view returns (INoteAdapter) {
        return _noteAdapters[lienToken];
    }

    function _processProceeds(uint256 amount) internal {}

    function registerNoteAdapter(address lienToken, address adapter) public {
        if (msg.sender != _owner) {
            revert Unauthorized();
        }
        _noteAdapters[lienToken] = INoteAdapter(adapter);
    }

    function createLoan(address lienToken, uint256 maintenanceId, uint256 seniorTrancheReturn, uint256 repayment) public {
        if (msg.sender != _owner) {
            revert Unauthorized();
        }
        _loans[lienToken][maintenanceId] = Loan({status: LoanStatus.Active, seniorTrancheReturn: seniorTrancheReturn, repayment: repayment});
    }

    function setAdminFeeRate(uint256 newRate) public {
        if (msg.sender != _owner) {
            revert Unauthorized();
        }
        _adminFeeRate = newRate;
    }

}
