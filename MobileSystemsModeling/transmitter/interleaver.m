%Прямое перемежение битовой последовательности
%   Входные аргументы:
%       inputBits - Числовой вектор.
%   Выходные аргументы:
%       interleavedBits - Числовой вектор - перемешанная битовая последовательность.
function interleavedBits = interleaver(inputbits)
    if ~isnumeric(inputbits) || ~isvector(inputbits) || any((inputbits ~= 0) & (inputbits ~=1))
        error('[Interleaver] Входные биты должны быть числовым вектором, содержащим только 0 и 1.');
    end

    permutationVector = randperm(length(inputbits));
    interleavedBits = inputbits(permutationVector);

    setappdata(0, 'permutationVector', permutationVector);
end