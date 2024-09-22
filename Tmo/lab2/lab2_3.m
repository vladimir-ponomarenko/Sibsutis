N = 800;     
K = 600;     
nu = 0;      
o = 1;      
l1 = 18;    
l2 = 80;    


W = o * randn(N, K);

RW = zeros(N, K);
RW(1, :) = W(1, :);
for n = 2:N
    RW(n, :) = RW(n-1, :) + W(n, :);
end

RW_damped = zeros(N, K);
RW_damped(1, :) = W(1, :);
for n = 2:N
    RW_damped(n, :) = 0.9 * RW_damped(n-1, :) + W(n, :);
end


figure;
plot(RW_damped);
xlabel('Отсчет времени (n)');
ylabel('Значение случайного блуждания');
title('Случайные блужданий с затуханием');


pairs1 = [10, 9; 50, 49; 100, 99; 200, 199];
pairs2 = [50, 40; 100, 90; 200, 190];
colors = ['r', 'g', 'b', 'm'];

figure;

subplot(1, 2, 1);
hold on;
for i = 1:size(pairs1, 1)
    ni = pairs1(i, 1);
    nj = pairs1(i, 2);
    scatter(RW_damped(ni, :), RW_damped(nj, :), 5, colors(i), 'filled');
end
xlabel('e[n_i]');
ylabel('e[n_j]');
title('Диаграммы рассеяния (лаг 1)');
legend('(10, 9)', '(50, 49)', '(100, 99)', '(200, 199)');

subplot(1, 2, 2);
hold on;
for i = 1:size(pairs2, 1)
    ni = pairs2(i, 1);
    nj = pairs2(i, 2);
    scatter(RW_damped(ni, :), RW_damped(nj, :), 5, colors(i), 'filled');
end
xlabel('e[n_i]');
ylabel('e[n_j]');
title('Диаграммы рассеяния (разные лаги)');
legend('(50, 40)', '(100, 90)', '(200, 190)');


r_e_hat_W = zeros(N-1, 1);   
r_e_hat_RW = zeros(N-1, 1);  
r_e_hat_RW_damped = zeros(N-1, 1); 

for n = 2:N 
    r_e_hat_W(n-1) = mean(W(n, :) .* W(n-1, :)); 
    r_e_hat_RW(n-1) = mean(RW(n, :) .* RW(n-1, :)); 
    r_e_hat_RW_damped(n-1) = mean(RW_damped(n, :) .* RW_damped(n-1, :)); 
end


r_e_theoretical_W = zeros(N-1, 1); 

r_e_theoretical_RW = (1:N-1)';  

r_e_theoretical_RW_damped = 0.9 * (o^2 / 0.19) * (1 - 0.81.^(0:N-2)');


figure;
subplot(3,1,1);
hold on;
plot(r_e_hat_W, 'b-', 'LineWidth', 2);         
plot(r_e_theoretical_W, 'r--', 'LineWidth', 2);   
xlabel('n');
ylabel('r_e(n, n-1)');
title('Автокорреляция белого шума');
legend('Выборочная АКФ', 'Теоретическая АКФ');
grid on;

subplot(3,1,2);
hold on;
plot(r_e_hat_RW, 'b-', 'LineWidth', 2);         
plot(r_e_theoretical_RW, 'r--', 'LineWidth', 2);  
xlabel('n');
ylabel('r_e(n, n-1)');
title('Автокорреляция случайного блуждания');
legend('Выборочная АКФ', 'Теоретическая АКФ');
grid on;

subplot(3,1,3);
hold on;
plot(r_e_hat_RW_damped, 'b-', 'LineWidth', 2);         
plot(r_e_theoretical_RW_damped, 'r--', 'LineWidth', 2);   
xlabel('n');
ylabel('r_e(n, n-1)');
title('Автокорреляция случайного блуждания с затуханием');
legend('Выборочная АКФ', 'Теоретическая АКФ');
grid on;


realization1 = 1;
realization2 = 2;

mean_time_l1_realization1 = mean(RW_damped(1:N-l1, realization1) .* RW_damped(l1+1:N, realization1));
mean_time_l2_realization1 = mean(RW_damped(1:N-l2, realization1) .* RW_damped(l2+1:N, realization1));

mean_time_l1_realization2 = mean(RW_damped(1:N-l1, realization2) .* RW_damped(l1+1:N, realization2));  
mean_time_l2_realization2 = mean(RW_damped(1:N-l2, realization2) .* RW_damped(l2+1:N, realization2));
mean_ensemble_l1 = r_e_hat_RW_damped(l1);
mean_ensemble_l2 = r_e_hat_RW_damped(l2);

theoretical_l1 = r_e_theoretical_RW_damped(l1);
theoretical_l2 = r_e_theoretical_RW_damped(l2);

fprintf('Лаг l1 = %d:\n', l1);
fprintf('  Среднее по времени : %f\n', mean_time_l1_realization1);
fprintf('  Среднее по времени : %f\n', mean_time_l1_realization2);
fprintf('  Среднее по ансамблю: %f\n', mean_ensemble_l1);
fprintf('  Теоретическое значение: %f\n\n', theoretical_l1);

fprintf('Лаг l2 = %d:\n', l2);
fprintf('  Среднее по времени (реализация 1): %f\n', mean_time_l2_realization1);
fprintf('  Среднее по времени (реализация 2): %f\n', mean_time_l2_realization2);
fprintf('  Среднее по ансамблю: %f\n', mean_ensemble_l2);
fprintf('  Теоретическое значение: %f\n\n', theoretical_l2);
