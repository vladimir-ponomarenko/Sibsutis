%Обратное перемежение битовой последовательности
%   Входные аргументы:
%       inputBits - Числовой вектор - перемешанная битовая последовательность.
%   Выходные аргументы:
%       deinterleavedBits - Числовой вектор - восстановленная битовая последовательность.
function deinterleavedBits = deinterleaver(inputBits)
    if ~isnumeric(inputBits) || ~isvector(inputBits) || any((inputBits ~= 0) & (inputBits ~= 1))
           error('[Deinterleaver] Входные биты должны быть числовым вектором, содержащим только 0 и 1.');
    end

    permutationVector = getappdata(0, 'permutationVector');

    if isempty(permutationVector)
        error('[Deinterleaver] Вектор перестановки не был сохранен.  Убедитесь, что прямой перемежитель был выполнен.');
    end

    deinterleavedBits = zeros(size(inputBits));
    deinterleavedBits(permutationVector) = inputBits;
end