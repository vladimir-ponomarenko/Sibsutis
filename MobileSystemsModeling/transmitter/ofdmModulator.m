%OFDMMODULATOR OFDM модуляция вектора QPSK символов.
%   ofdmSymbol = OFDMMODULATOR(qpskSymbols, params) формирует OFDM символ
%   из вектора QPSK символов 'qpskSymbols' с использованием параметров,
%   заданных в структуре 'params'.
function ofdmSymbol = ofdmModulator(qpskSymbols, params)
    if ~isnumeric(qpskSymbols) || ~isvector(qpskSymbols)
        error('[OFDM Modulator] Входные QPSK символы должны быть числовым вектором.');
    end
    if ~isstruct(params)
        error('[OFDM Modulator] Параметры должны быть переданы в виде структуры.');
    end
    requiredFields = {'rsStep', 'cpLengthRatio', 'zeroPaddingRatio'};
    for i = 1:length(requiredFields)
        if ~isfield(params, requiredFields{i})
            error('[OFDM Modulator] В структуре параметров отсутствует поле ''%s''.', requiredFields{i});
        end
    end

    Nqpsk = length(qpskSymbols);
    rsStep = params.rsStep;

    if rsStep <= 1
        error('[OFDM Modulator] rsStep должен быть больше 1.');
    end

    Nrs_calc = ceil(Nqpsk / (rsStep - 1));
    if Nqpsk == 0
        Nrs_calc = 0;
    end
    
    Nactive = Nqpsk + Nrs_calc;

    if Nactive > 0 && rsStep <= Nactive
       rsIndices = 1:rsStep:Nactive;
    else
       rsIndices = [];
    end
    
    Nrs = length(rsIndices);
    Nactive = Nqpsk + Nrs;
    
    if ~isempty(rsIndices)
       rsIndices = rsIndices(rsIndices <= Nactive);
    end
    
    referenceSignal = (0.707 + 0.707j) * ones(1, Nrs);

    if Nactive > 0
        allIndices = 1:Nactive;
        dataIndices = setdiff(allIndices, rsIndices);
    else
        dataIndices = [];
    end

    if length(dataIndices) ~= Nqpsk
         error('[OFDM Modulator] Внутренняя ошибка: Несоответствие между индексами данных (%d) и Nqpsk (%d). Nactive=%d, Nrs=%d, rsStep=%d', ...
               length(dataIndices), Nqpsk, Nactive, Nrs, rsStep);
    end

     ofdmSpectrum = zeros(1, Nactive);
     if Nrs > 0
        ofdmSpectrum(rsIndices) = referenceSignal;
     end
     if Nqpsk > 0
        ofdmSpectrum(dataIndices) = qpskSymbols;
     end

    Nzero = round(params.zeroPaddingRatio * Nactive);
    ofdmSpectrum = [zeros(1, Nzero), ofdmSpectrum, zeros(1, Nzero)];
    timeDomainSignal = ifft(ofdmSpectrum);

    Nfft = length(timeDomainSignal);
    cpLength = round(Nfft * params.cpLengthRatio);
    cpLength = min(cpLength, Nfft);

    if cpLength > 0
        cyclicPrefix = timeDomainSignal(end-cpLength+1:end);
        ofdmSymbol = [cyclicPrefix, timeDomainSignal];
    else
        ofdmSymbol = timeDomainSignal;
    end


    setappdata(0, 'referenceSignal', referenceSignal);
    setappdata(0, 'rsIndices', rsIndices);
    setappdata(0, 'Nzero', Nzero);
    setappdata(0, 'Nrs', Nrs);
    setappdata(0, 'Nqpsk', Nqpsk);
    setappdata(0, 'cpLength', cpLength);
    setappdata(0, 'Nactive', Nactive);
end