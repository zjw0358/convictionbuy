'''
#
# TD Ameritrade IP Company, Inc. (c) 2011-2015
#

script VariableMax {
    input price = close;
    input min = 0;
    input max = 0;
    input maxOffset = 0;
    plot VMax = fold i = min to max with m = Double.NEGATIVE_INFINITY do Max(m, getValue(price, i, maxOffset));
}

script VariableMin {
    input price = close;
    input min = 0;
    input max = 0;
    input maxOffset = 0;
    plot VMin = fold i = min to max with m = Double.POSITIVE_INFINITY do Min(m, getValue(price, i, maxOffset));
}

script DX {
    input DXPlus = close;
    input DXMinus = close;
    input min = 0;
    input max = 0;
    input maxOffset = 0;

    def SumDXPlus = fold i = min to max with p do p + getValue(DXPlus, i, maxOffset);
    def SumDXMinus = fold j = min to max with m do m + getValue(DXMinus, j, maxOffset);
    plot DX = AbsValue(SumDXPlus - SumDXMinus) / (SumDXPlus + SumDXMinus + 0.000000001) * 100;
}

input price = close;
input minLength = 20;
input maxLength = 252;
input factor = 2.0;

assert(minLength > 0, "'min length' must be positive: " + minLength);
assert(factor >= 1, "'factor' must be greater than or equal to 1: " + factor);

def rawOffset = fold i = minLength to maxLength with off = -1 do if off == -1 and getValue(price, i, maxLength) > price * factor then i else off;
def offset = if IsNaN(rawOffset) then -1 else rawOffset;

def logPrice = log(price);

def B2Offset = if offset < 0 then -1 else round(offset * 0.6, 0);

def DXPlus = Max(logPrice - logPrice[1], 0);
def DXMinus = Max(logPrice[1] - logPrice, 0);
def DX1 = DX(DXPlus, DXMinus, B2Offset + 1, offset + 1, maxLength);
def DX2 = DX(DXPlus, DXMinus, 0, B2Offset + 1, maxLength);

def B3Offset = if offset < 0 then -1 else round(offset * 0.4, 0);
def highestB2toB3 = VariableMax(logPrice, B3Offset + 1, B2Offset + 1, maxLength);
def highestB3toB5 = VariableMax(logPrice, 0, B3Offset + 1, maxLength);

def hiLogPrice = if IsNaN(getValue(logPrice, offset, maxLength)) then logPrice else getValue(logPrice, offset, maxLength);
def loLogPrice = VariableMin(logPrice, 0, offset + 1, maxLength);
def L2 = loLogPrice * 0.6 + hiLogPrice * 0.4;
def L3 = loLogPrice * 0.4 + hiLogPrice * 0.6;

plot SemiCup = offset > 0 and DX1 > 25 and DX2 < 25 and highestB2toB3 < L3 and highestB3toB5 < L2;

# find last cup
def curBar = barNumber();
def cupEnd = HighestAll(if SemiCup then curBar else Double.NaN);

def rawCupOffset = HighestAll(if cupEnd == curBar and SemiCup then offset else Double.NaN);
def cupOffset = if IsNaN(rawCupOffset) then 0 else rawCupOffset;

def cupHiLogPrice = HighestAll(if curBar == cupEnd then getValue(logPrice, cupOffset, maxLength) else Double.NaN);
def cupLowLogPrice = HighestAll(if curBar == cupEnd then VariableMin(logPrice, 0, cupOffset + 1, maxLength) else Double.NaN);

def found = curBar >= cupEnd - cupOffset and curBar <= cupEnd;

# cup visualization
def hi = exp(cupHiLogPrice);
def lo = exp(cupLowLogPrice);
def t = curBar - cupEnd;
def dev = (hi - lo) * Power(t / cupOffset, 10);
plot Curve = if found then Min(hi, dev + 0.98 * lo) else Double.NaN;

AddLabel(cupOffset, "Semi-Cup formation size: " + (cupOffset + 1));
SemiCup.SetPaintingStrategy(PaintingStrategy.BOOLEAN_POINTS);
SemiCup.SetLineWeight(3);
SemiCup.SetLineWeight(3);
Curve.SetDefaultColor(GetColor(2));
'''