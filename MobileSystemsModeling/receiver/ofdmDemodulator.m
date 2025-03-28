%OFDMDEMODULATOR OFDM демодуляция принятого сигнала с оценкой канала и эквалайзацией.
function qpskSymbolsOut = ofdmDemodulator(receivedSignal)
    cpLength = getappdata(0, 'cpLength');
    Nzero = getappdata(0, 'Nzero');
    rsIndices = getappdata(0, 'rsIndices');
    referenceSignal = getappdata(0, 'referenceSignal');
    Nqpsk = getappdata(0, 'Nqpsk');
    Nrs = getappdata(0, 'Nrs');

    if isempty(cpLength) || isempty(Nzero) || isempty(rsIndices) || isempty(referenceSignal) || isempty(Nqpsk) || isempty(Nrs)
         error('[OFDM Demodulator] Не удалось получить параметры, сохраненные модулятором. Убедитесь, что ofdmModulator был выполнен.');
    end

    if ~isnumeric(receivedSignal) || ~isvector(receivedSignal)
        error('[OFDM Demodulator] Принятый сигнал должен быть числовым вектором.');
    end
    expectedMinLength = cpLength + Nqpsk + Nrs + 2*Nzero;

    signalLength = length(receivedSignal);
    if signalLength > expectedMinLength
        cpPart = receivedSignal(1:cpLength);
        corr = zeros(1, signalLength - cpLength + 1);
        for i = 1:length(corr)
            corr(i) = abs(sum(conj(cpPart) .* receivedSignal(i:i+cpLength-1)));
        end
        [~, startIdx] = max(corr);
        receivedSignal = receivedSignal(startIdx:startIdx+expectedMinLength-1);
    end

    if length(receivedSignal) ~= expectedMinLength
        warning('[OFDM Demodulator] Длина принятого сигнала (%d) не совпадает с ожидаемой (%d).', length(receivedSignal), expectedMinLength);
    end

    signalWithoutCP = receivedSignal(cpLength+1:end);
    ofdmSpectrum = fft(signalWithoutCP);
    C = ofdmSpectrum(Nzero+1:end-Nzero);

    if length(C) ~= (Nqpsk + Nrs)
         error('[OFDM Demodulator] Размер спектра активных поднесущих (%d) не совпадает с ожидаемым (%d).', length(C), Nqpsk + Nrs);
    end

    receivedReferenceSignal = C(rsIndices);
    H = receivedReferenceSignal ./ referenceSignal;
    indicesAll = 1:length(C);
    H_interpolated = interp1(rsIndices, H, indicesAll, 'spline');

    epsilon = 1e-10;
    Ceq = C ./ (H_interpolated + epsilon);

    dataIndices = setdiff(indicesAll, rsIndices);
    qpskSymbolsOut = Ceq(dataIndices);

    setappdata(0, 'ofdmSpectrum_C', C);
    setappdata(0, 'channelEstimate_H_interp', H_interpolated);
    setappdata(0, 'equalizedSpectrum_Ceq', Ceq);
end