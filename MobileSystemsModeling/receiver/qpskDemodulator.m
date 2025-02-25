%QPSKDEMODULATOR QPSK демодуляция комплексных символов.
%   demodulatedBits = QPSKDEMODULATOR(receivedSymbols) преобразует входной
%   вектор комплексных символов 'receivedSymbols' в битовую
%   последовательность 'demodulatedBits', используя QPSK демодуляцию.
function demodulatedBits = qpskDemodulator(receivedSymbols)
    if ~isnumeric(receivedSymbols) || ~isvector(receivedSymbols)
        error('[QPSK Demodulator] Входные символы должны быть числовым вектором.');
    end

    numSymbols = length(receivedSymbols);
    demodulatedBits = zeros(1, 2 * numSymbols);

    for i = 1:numSymbols
        realPart = real(receivedSymbols(i));
        imagPart = imag(receivedSymbols(i));

        if realPart >= 0 && imagPart >= 0
            demodulatedBits(2*i-1:2*i) = [0 0];
        elseif realPart >= 0 && imagPart < 0
            demodulatedBits(2*i-1:2*i) = [0 1];
        elseif realPart < 0 && imagPart >= 0
            demodulatedBits(2*i-1:2*i) = [1 0];
        elseif realPart < 0 && imagPart < 0
            demodulatedBits(2*i-1:2*i) = [1 1];
        end
    end
end