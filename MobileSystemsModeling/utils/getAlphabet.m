%Возвращает алфавит и количество бит на символ.
function[alphabet, bitPerSymbol] = getAlphabet()
    alphabet = ['a':'z', 'A':'Z', '0':'9', ' ', '.'];
    bitPerSymbol = ceil(log2(length(alphabet)));
end