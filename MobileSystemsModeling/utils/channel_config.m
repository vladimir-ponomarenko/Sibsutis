%CHANNEL_CONFIG Возвращает структуру с параметрами канала.
function params = channel_config()
    params.numRays = 7;
    params.noisePowerBW = -120;

    params.bandwidth = 13e6;
    params.carrierFrequency = 1.9e9;

    params.c = 3e8;
end