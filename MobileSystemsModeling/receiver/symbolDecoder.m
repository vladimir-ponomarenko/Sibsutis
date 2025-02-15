%Декодирование битовой последовательности.
%   Входные аргументы:
%       encodedBits - Числовой вектор (содержащий 0 и 1) - закодированное сообщение.
%   Выходные аргументы:
%       decodedMessage - Вектор символов (строка) - декодированное сообщение.
function decodedMessage = symbolDecoder(encodedBits)
    [alphabet, bitsPerSymbol] = getAlphabet();

    if ~isnumeric(encodedBits) || ~isvector(encodedBits) || any((encodedBits ~= 0) & (encodedBits ~= 1))
        error('[SymbolDecoder] Входные биты должны быть числовым вектором, содержащим только 0 и 1.');
    end

    numSymbols = length(encodedBits)/bitsPerSymbol;
    if rem(length(encodedBits), bitsPerSymbol) ~= 0
        warning('[SymbolDecoder] Длина входной битовой последовательности не кратна количеству бит на символ. Лишние биты будут проигнорированы.');
        numSymbols = floor(numSymbols);
    end

    decodedMessage = '';
    for i = 1:numSymbols
        symbolBits = encodedBits((i-1)*bitsPerSymbol+1 : i*bitsPerSymbol);
        decimalValue = bi2de(symbolBits, 'left-msb');
        alphabetCharIndex = decimalValue + 1;

        if alphabetCharIndex > 0 && alphabetCharIndex <= length(alphabet)
            decodedMessage = [decodedMessage, alphabet(alphabetCharIndex)];
        else
            decodedMessage = [decodedMessage, '?'];
        end
    end 

end