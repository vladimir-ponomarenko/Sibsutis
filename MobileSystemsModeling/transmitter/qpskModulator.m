%QPSKMODULATOR QPSK модуляция битовой последовательности.
%   modulatedSymbols = QPSKMODULATOR(inputBits) преобразует входную
%   битовую последовательность 'inputBits' в вектор комплексных
%   символов 'modulatedSymbols', используя QPSK модуляцию.
function modulatedSymbols = qpskModulator(inputBits)
    if ~isnumeric(inputBits) || ~isvector(inputBits) || any((inputBits ~= 0) & (inputBits ~= 1))
        error('[QPSK Modulator] Входные биты должны быть числовым вектором, содержащим только 0 и 1.');
    end

    if mod(length(inputBits), 2) ~= 0
        warning('[QPSK Modulator] Длина входной битовой последовательности нечетная. Добавляем 0 в конец.');
        inputBits = [inputBits, 0]; 
    end

    numSymbols = length(inputBits) / 2;
    modulatedSymbols = zeros(1, numSymbols);
    for i = 1:numSymbols
        bit1 = inputBits(2*i-1);
        bit2 = inputBits(2*i);

       if bit1 == 0 && bit2 == 0
            modulatedSymbols(i) = 0.707 + 0.707j; % 00 -> 0.707 + 0.707j
        elseif bit1 == 0 && bit2 == 1
            modulatedSymbols(i) = 0.707 - 0.707j; % 01 -> 0.707 - 0.707j
        elseif bit1 == 1 && bit2 == 0
            modulatedSymbols(i) = -0.707 + 0.707j; % 10 -> -0.707 + 0.707j
        elseif bit1 == 1 && bit2 == 1
            modulatedSymbols(i) = -0.707 - 0.707j; % 11 -> -0.707 - 0.707j
       end
    end
end