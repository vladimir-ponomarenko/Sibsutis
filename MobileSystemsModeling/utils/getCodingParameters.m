%Возвращает параметры сверточного кодера.
%       constraintLength - Длина кодового ограничения.
%       codeGenerator    - Вектор генераторных полиномов (в восьмеричной форме).
function[constraintLength, codeGenerator] = getCodingParameters()
    constraintLength = 7;
    codeGenerator = [171, 133];
end