%OFDM_CONFIG Возвращает структуру с параметрами OFDM модулятора.
function params = ofdm_config()
    params.rsStep = 4;
    params.cpLengthRatio = 1/8;
    params.zeroPaddingRatio = 1/4;
end