%Знаковое кодирование текстового сообщения.
%   Входные аргументы:
%       message - Вектор символов - текстовое сообщение.
%   Выходные аргументы:
%       encodedBits - Числовой вектор (содержащий 0 и 1) - закодированное сообщение.
function encodedBits = symbolEncoder(message)
    [alphabet, bitsPerSymbol] = getAlphabet();

    if ~ischar(message) || ~isvector(message)
        error('[SymbolEncoder] Входное сообщение на должно быть вектором символов.');
    end

    encodedBits = [];
    for i = 1:length(message)
        alphabetCharIndex = find(alphabet == message(i));

        if isempty(alphabetCharIndex)
            error('[SymbolEncoder] Символ %s отсутствует в алфавите.', message(i));
        end

    decimalValue = alphabetCharIndex(1) - 1;
    binaryValue = de2bi(decimalValue, bitsPerSymbol, 'left-msb');
    encodedBits = [encodedBits, binaryValue];
    end
end