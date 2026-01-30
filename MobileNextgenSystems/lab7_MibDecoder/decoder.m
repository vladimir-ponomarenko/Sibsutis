clear; clc; close all;

% sample rate
sr = 10.0e6;

%% 1. Загрузка файла
filename = 'lte10Msps_g30_uz_f806MHz_r1.bin';
fprintf('Загрузка файла: %s\n', filename);

if ~isfile(filename)
    error('Файл не найден!'); 
end

fid = fopen(filename, 'rb');
raw_data = fread(fid, [2, inf], 'float32');
fclose(fid);
eNodeBOutput = complex(raw_data(1,:), raw_data(2,:)).';

spectrumScope = dsp.SpectrumAnalyzer('SampleRate', sr, ...
    'Title', 'Спектр принятого сигнала', 'ShowLegend', false);
spectrumScope(eNodeBOutput);

%% 2. Поиск ячейки
fprintf('--- Поиск ячейки и синхронизация ---\n');

enb = struct;
% Ресурсные блоки
enb.NDLRB = 6;
ofdmInfo = lteOFDMInfo(setfield(enb, 'CyclicPrefix', 'Normal'));

downsampled = resample(eNodeBOutput, ofdmInfo.SamplingRate, round(sr));

searchalg.MaxCellCount = 1;
searchalg.SSSDetection = 'PostFFT';

enb.DuplexMode = 'FDD'; 
enb.CyclicPrefix = 'Normal'; 

[cellID, offset, peak] = lteCellSearch(enb, downsampled, searchalg);
enb.NCellID = cellID;

[~, corr_vec] = lteDLFrameOffset(enb, downsampled); 
downsampled = downsampled(1+offset:end); 
enb.NSubframe = 0;

%% 3. Обработка сигнала
delta_f = lteFrequencyOffset(enb, downsampled);
downsampled = lteFrequencyCorrect(enb, downsampled, delta_f);

rxgrid = lteOFDMDemodulate(enb, downsampled);

cec = struct('PilotAverage','UserDefined','FreqWindow',13,'TimeWindow',9,...
    'InterpType','cubic','InterpWindow','Centered','InterpWinSize',1);
enb.CellRefP = 4; 
[hest, nest] = lteDLChannelEstimate(enb, cec, rxgrid);

%% 4. Декодирование MIB
fprintf('--- Декодирование MIB ---\n');
pbchIndices = ltePBCHIndices(enb);
[pbchRx, pbchHest] = lteExtractResources(pbchIndices, rxgrid, hest);

[bchBits, pbchSymbols, nfmod4, mib, enb.CellRefP] = ltePBCHDecode(enb, pbchRx, pbchHest, nest);
enb = lteMIB(mib, enb);
enb.NFrame = enb.NFrame + nfmod4;

%% 4.1 Фильтрация созвездия
fprintf('--- Пост-обработка созвездия ---\n');

ideal_QPSK = [1+1i, 1-1i, -1+1i, -1-1i] / sqrt(2);
distances = min(abs(pbchSymbols - ideal_QPSK), [], 2);
thresh_dist = 0.5;
thresh_zero = 0.1;
valid_mask = (distances < thresh_dist) & (abs(pbchSymbols) > thresh_zero);
pbchSymbols_clean = pbchSymbols(valid_mask);

fprintf('  [i] Отфильтровано символов: %d (из %d)\n', length(pbchSymbols_clean), length(pbchSymbols));

%% 5. Вывод
clc;
fprintf('\n==================================================\n');
fprintf('           LTE DETECTED INFO                      \n');
fprintf('==================================================\n');
fprintf('Physical Layer:\n');
fprintf('  [+] Cell ID        : %d\n', enb.NCellID);
fprintf('  [+] Duplex Mode    : %s\n', enb.DuplexMode);
fprintf('  [+] Cyclic Prefix  : %s\n', enb.CyclicPrefix);
fprintf('  [+] Freq Offset    : %.2f Hz\n', delta_f);
fprintf('--------------------------------------------------\n');
fprintf('Master Information Block:\n');
fprintf('  [+] Bandwidth      : %d RBs (%.1f MHz)\n', enb.NDLRB, enb.NDLRB/5);
fprintf('  [+] SFN            : %d\n', enb.NFrame);
fprintf('  [+] TX Antennas    : %d\n', enb.CellRefP);
fprintf('  [+] PHICH Duration : %s\n', enb.PHICHDuration);
fprintf('  [+] PHICH Ng       : %s\n', enb.Ng);
fprintf('==================================================\n');

%% 6. Графики
hFig = figure(1);
set(hFig, 'Name', 'LTE Signal Analysis', 'Color', 'w', 'Position', [100, 100, 1000, 700]);

subplot(2,2,1);
plot(abs(corr_vec), 'LineWidth', 1.5);
title('1. PSS/SSS Correlation Peak');
xlabel('Samples'); ylabel('Magnitude');
grid on; xlim([0 length(corr_vec)]);

subplot(2,2,2);
surf(abs(hest(:,:,1,1))); 
view(2); shading flat; colormap('jet');
title('2. Channel Estimate');
xlabel('OFDM Symbols'); ylabel('Subcarriers');
colorbar;

subplot(2,2,3);
plot(pbchSymbols_clean, '.', 'MarkerSize', 8);
title('3. PBCH Constellation (Filtered QPSK)');
grid on; axis square;
xlim([-1.5 1.5]); ylim([-1.5 1.5]);
xlabel('In-Phase (I)'); ylabel('Quadrature (Q)');
hold on; 
plot([1 -1 1 -1]/sqrt(2), [1 1 -1 -1]/sqrt(2), 'rx', 'LineWidth', 2, 'MarkerSize', 10);
legend('Received', 'Ideal');

subplot(2,2,4);
imagesc(abs(rxgrid(:,:,1)));
title('4. Resource Grid (Subframe 0)');
xlabel('OFDM Symbols'); ylabel('Subcarriers');
colormap('parula');
colorbar;