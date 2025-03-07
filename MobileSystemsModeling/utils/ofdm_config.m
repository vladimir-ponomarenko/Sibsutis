%OFDM_CONFIG Возвращает структуру с параметрами OFDM модулятора.
function params = ofdm_config()
    params.rsStep = 6;
    params.cdLengthRatio = 1/16;
    params.zeroPaddingRatio = 1/4;
end