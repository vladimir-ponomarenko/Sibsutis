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
    Nrs = floor(Nqpsk / params.rsStep); % Количество опорных поднесущих
    referenceSignal = (0.707 + 0.707j) * ones(1, Nrs); % Опорный сигнал
    rsIndices = 1:params.rsStep:(Nqpsk + Nrs); % Индексы опорных поднесущих
    
     if ~isempty(rsIndices) && rsIndices(end) > Nqpsk + Nrs
         rsIndices = rsIndices(1:end-1);
         Nrs = length(rsIndices);
         referenceSignal = (0.707 + 0.707j) * ones(1, Nrs);
     end

    % Размещение опорного сигнала
    ofdmSpectrum = zeros(1, Nqpsk + Nrs);
    dataIndices = setdiff(1:(Nqpsk + Nrs), rsIndices);

    ofdmSpectrum(rsIndices) = referenceSignal;
    ofdmSpectrum(dataIndices) = qpskSymbols;

    % Защитный интревал из нулей
    Nzero = round(params.zeroPaddingRatio * (Nqpsk + Nrs));
    ofdmSpectrum = [zeros(1, Nzero), ofdmSpectrum, zeros(1, Nzero)];

    timeDomainSignal = ifft(ofdmSpectrum);

    % Циклический префикс
    cpLength = round(length(timeDomainSignal) * params.cpLengthRatio);
    cyclicPrefix = timeDomainSignal(end-cpLength+1:end);
    ofdmSymbol = [cyclicPrefix, timeDomainSignal];

    setappdata(0, 'referenceSignal', referenceSignal);
    setappdata(0, 'rsIndices', rsIndices);
    setappdata(0, 'Nzero', Nzero);
    setappdata(0, 'Nrs', Nrs);
    setappdata(0, 'Nqpsk', Nqpsk);
    setappdata(0, 'cpLength', cpLength);
end