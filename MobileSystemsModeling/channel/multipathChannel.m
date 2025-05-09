%receivedSignal = MULTIPATHCHANNEL(transmittedSignal, params)
%   моделирует прохождение сигнала 'transmittedSignal' через многолучевой
%   канал и добавляет аддитивный белый гауссов шум (АБГШ).
function receivedSignal = multipathChannel(transmittedSignal, params)
    if ~isnumeric(transmittedSignal) || ~isvector(transmittedSignal)
        error('[Multipath Channel] Переданный сигнал должен быть числовым вектором.');
    end
    if ~isstruct(params)
        error('[Multipath Channel] Параметры канала должны быть переданы в виде структуры.');
    end
    requiredFields = {'numRays', 'noisePowerBW', 'bandwidth', 'carrierFrequency', 'c'};
    for i = 1:length(requiredFields)
        if ~isfield(params, requiredFields{i})
            error('[Multipath Channel] В структуре параметров отсутствует поле ''%s''.', requiredFields{i});
        end
    end
    if ~license('test', 'communication_toolbox')
        error('[Multipath Channel] Communications Toolbox is required for wgn function.');
    end

    L = length(transmittedSignal);
    Ts = 1/params.bandwidth;
    D = randi([10,500], 1, params.numRays);

    [Dmin, ~] = min(D);
    tau_sec = (D - Dmin) / params.c;
    tau_samples = round(tau_sec / Ts);
    G = params.c ./ (4 * pi * D * params.carrierFrequency);
    max_tau = max(tau_samples);
    delayedSignals = zeros(params.numRays, L + max_tau);

    for i = 1:params.numRays
        startIndex = tau_samples(i) + 1;
        endIndex = tau_samples(i) + L;
        delayedSignals(i, startIndex:endIndex) = transmittedSignal * G(i);
    end

    multipathChannel = sum(delayedSignals, 1);
    noise = wgn(1, length(multipathChannel), params.noisePowerBW, [], 'complex');
    noisySignal = multipathChannel + noise;

    receivedSignal = noisySignal;
end