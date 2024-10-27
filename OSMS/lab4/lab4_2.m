% Параметры последовательностей Голда
SIZE = 5;
length_seq = 2^SIZE - 1;

% Начальные состояния регистров
regs = {
    [0, 1, 1, 0, 0], [1, 0, 0, 1, 1];  
    [0, 1, 1, 0, 1], [0, 1, 1, 1, 0]   
};

% Генерация последовательностей Голда
[gold_seq1, reg1_final] = generate_sequence(regs{1,1}, regs{1,2}, length_seq);
[gold_seq2, reg2_final] = generate_sequence(regs{2,1}, regs{2,2}, length_seq);

fprintf('Первая последовательность Голда (x = 12, y = 19):\n');
fprintf('Последовательность Голда: %s\n\n', num2str(gold_seq1));
fprintf('Вторая последовательность Голда (x = 13, y = 14):\n');
fprintf('Последовательность Голда: %s\n\n', num2str(gold_seq2));

% Вычисление корреляций
[cor1, lag1] = xcorr(gold_seq1, 'normalized');
[cor2, lag2] = xcorr(gold_seq2, 'normalized');
[cross_cor, lag_cross] = xcorr(gold_seq1, gold_seq2, 'normalized');

positive_lag_idx = lag1 >= 0 & lag1 <= 31;

figure('Name', 'Корреляции последовательностей Голда');

subplot(3,1,1);
stem(lag1(positive_lag_idx), cor1(positive_lag_idx));
title('Автокорреляция первой последовательности');
xlabel('Задержка (лаг)');
ylabel('Значение автокорреляции');
xlim([0, 30]); 

subplot(3,1,2);
stem(lag2(positive_lag_idx), cor2(positive_lag_idx));
title('Автокорреляция второй последовательности');
xlabel('Задержка (лаг)');
ylabel('Значение автокорреляции');
xlim([0, 30]);

subplot(3,1,3);
stem(lag_cross(positive_lag_idx), cross_cor(positive_lag_idx));
title('Взаимная корреляция последовательностей');
xlabel('Задержка (лаг)');
ylabel('Значение взаимной корреляции');
xlim([0, 30]);

fprintf('\n--- Значения автокорреляции первой последовательности ---\n');
for i = find(positive_lag_idx) 
    fprintf('Задержка %d: %.3f\n', lag1(i), cor1(i));
end

fprintf('\n--- Значения автокорреляции второй последовательности ---\n');
for i = find(positive_lag_idx)
    fprintf('Задержка %d: %.3f\n', lag2(i), cor2(i));
end

fprintf('\n--- Значения взаимной корреляции ---\n');
for i = find(positive_lag_idx)
    fprintf('Задержка %d: %.3f\n', lag_cross(i), cross_cor(i));
end


% Функция генерации последовательности
function [seq, reg_final] = generate_sequence(reg_x, reg_y, length)
    seq = zeros(1, length);
    for i = 1:length
        seq(i) = mod(reg_x(end) + reg_y(end), 2);
        [reg_x, reg_y] = shift_registers(reg_x, reg_y);
    end
    reg_final = {reg_x, reg_y};
end

% Функция сдвига регистров
function [reg_x, reg_y] = shift_registers(reg_x, reg_y)
    reg_x = [mod(reg_x(4) + reg_x(5), 2), reg_x(1:end-1)];
    reg_y = [mod(reg_y(3) + reg_y(5), 2), reg_y(1:end-1)];
end
