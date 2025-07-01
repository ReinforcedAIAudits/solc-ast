pragma solidity ^0.8.30;

interface IUniswapV3Pool {
    function observe(uint32[] calldata secondsAgos) external view returns (int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s);

    function slot0() external view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked);
}

contract DynamicPriceOracle {
    IUniswapV3Pool public pool;
    address public quoteToken;
    uint32 public maPeriod;
    mapping(address => uint256) public lastUpdateTimestamp;
    mapping(address => uint256) public priceHistory;
    uint256 public constant PRICE_DEVIATION_THRESHOLD = 500;

    event PriceUpdated(address indexed token, uint256 newPrice, uint256 timestamp);
    event PoolChanged(address indexed oldPool, address indexed newPool);

    constructor(address _pool, address _quoteToken, uint32 _maPeriod) {
        pool = IUniswapV3Pool(_pool);
        quoteToken = _quoteToken;
        maPeriod = _maPeriod;
    }

    function getOldestObservationSecondsAgo(IUniswapV3Pool _pool) internal view returns (uint32 secondsAgo) {
        (, , uint16 observationIndex, uint16 observationCardinality, , , ) = _pool.slot0();
        if (observationCardinality <= 1) {
            return 0;
        }
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = 0;
        secondsAgos[1] = type(uint32).max;

        try _pool.observe(secondsAgos) returns (int56[] memory tickCumulatives, uint160[] memory) {
            if (tickCumulatives.length >= 2) {
                return 3600;
            }
        }
        catch {
            return 0;
        }

        return 3600;
    }

    function consult(IUniswapV3Pool _pool, uint32 _period) internal view returns (int24 timeWeightedAverageTick, uint128 harmonicMeanLiquidity) {
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = _period;
        secondsAgos[1] = 0;

        (int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s) = _pool.observe(secondsAgos);

        int56 tickCumulativesDelta = tickCumulatives[1] - tickCumulatives[0];
        uint160 secondsPerLiquidityCumulativesDelta = secondsPerLiquidityCumulativeX128s[1] - secondsPerLiquidityCumulativeX128s[0];

        timeWeightedAverageTick = int24(tickCumulativesDelta / int56(uint56(_period)));
        harmonicMeanLiquidity = uint128(uint256(_period) << 128) / uint128(secondsPerLiquidityCumulativesDelta);
    }

    function getQuoteAtTick(int24 _tick, uint128 _baseAmount, address _baseToken, address _quoteToken) internal pure returns (uint256 quoteAmount) {
        uint160 sqrtRatioX96 = getSqrtRatioAtTick(_tick);

        if (_baseToken < _quoteToken) {
            quoteAmount = mulDiv(uint256(_baseAmount), uint256(sqrtRatioX96) * uint256(sqrtRatioX96), 1 << 192);
        } else {
            quoteAmount = mulDiv(1 << 192, uint256(_baseAmount), uint256(sqrtRatioX96) * uint256(sqrtRatioX96));
        }
    }

    function getSqrtRatioAtTick(int24 tick) internal pure returns (uint160 sqrtPriceX96) {
        uint256 absTick = tick < 0 ? uint256(-int256(tick)) : uint256(int256(tick));

        uint256 ratio = absTick & 0x1 != 0 ? 0xfffcb933bd6fad37aa2d162d1a594001 : 0x100000000000000000000000000000000;
        if (absTick & 0x2 != 0) {
            ratio = (ratio * 0xfff97272373d413259a46990580e213a) >> 128;
        }
        if (absTick & 0x4 != 0) {
            ratio = (ratio * 0xfff2e50f5f656932ef12357cf3c7fdcc) >> 128;
        }

        if (tick > 0) {
            ratio = type(uint256).max / ratio;
        }

        sqrtPriceX96 = uint160((ratio >> 32) + (ratio % (1 << 32) == 0 ? 0 : 1));
    }

    function mulDiv(uint256 a, uint256 b, uint256 denominator) internal pure returns (uint256 result) {
        uint256 prod0;
        uint256 prod1;
        assembly {
            prod0 := mul(a, b)
            prod1 := sub(sub(mulmod(a, b, not(0)), prod0), lt(mulmod(a, b, not(0)), prod0))
        }

        if (prod1 == 0) {
            require(denominator > 0);
            assembly { result := div(prod0, denominator) }
            return result;
        }

        require(denominator > prod1);

        uint256 remainder;
        assembly {
            remainder := mulmod(a, b, denominator)
            prod1 := sub(prod1, gt(remainder, prod0))
            prod0 := sub(prod0, remainder)
        }

        uint256 twos = denominator & (~denominator + 1);
        assembly {
            denominator := div(denominator, twos)
            prod0 := div(prod0, twos)
            twos := add(div(sub(0, twos), twos), 1)
        }

        prod0 |= prod1 * twos;

        uint256 inverse = (3 * denominator) ^ 2;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;

        result = prod0 * inverse;
        return result;
    }

    function getMovingAveragePrice(address _tokenA, uint128 _tokenAPrecision) internal view returns (uint256) {
        uint32 oldestObservationSecondsAgo = getOldestObservationSecondsAgo(pool);
        uint32 period = maPeriod < oldestObservationSecondsAgo ? maPeriod : oldestObservationSecondsAgo;

        (int24 timeWeightedAverageTick, ) = consult(pool, period);

        uint256 tokenBPerTokenA = getQuoteAtTick(timeWeightedAverageTick, _tokenAPrecision, _tokenA, quoteToken);

        return tokenBPerTokenA;
    }

    function updateTokenPrice(address _token, uint128 _precision) external {
        uint256 newPrice = getMovingAveragePrice(_token, _precision);
        uint256 oldPrice = priceHistory[_token];

        if (oldPrice > 0) {
            uint256 deviation = oldPrice > newPrice ? ((oldPrice - newPrice) * 10000) / oldPrice : ((newPrice - oldPrice) * 10000) / oldPrice;
            require(deviation <= PRICE_DEVIATION_THRESHOLD, "Price deviation too high");
        }

        priceHistory[_token] = newPrice;
        lastUpdateTimestamp[_token] = block.timestamp;

        emit PriceUpdated(_token, newPrice, block.timestamp);
    }

    function setMovingAveragePeriod(uint32 _newPeriod) external {
        require(_newPeriod > 0 && _newPeriod <= 86400, "Invalid period");
        maPeriod = _newPeriod;
    }

    function changePool(address _newPool) external {
        require(_newPool != address(0), "Invalid pool address");
        address oldPool = address(pool);
        pool = IUniswapV3Pool(_newPool);
        emit PoolChanged(oldPool, _newPool);
    }
}