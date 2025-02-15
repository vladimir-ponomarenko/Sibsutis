%Сверточное кодировние.
function encodedBits = convolutionalEncoder(inputBits)

    if ~isnumeric(inputBits) || ~isvector(inputBits) || any((inputBits ~= 0) & (inputBits ~= 1))
        error('[ConvolutionalEncoder] Входные биты должны быть числовым вектором, содержащим только 0 и 1.');
    end 

    [constraintLength, codeGenerator] = getCodingParameters();
    trellis = poly2trellis(constraintLength, codeGenerator);
    encodedBits = convenc(inputBits, trellis);

end