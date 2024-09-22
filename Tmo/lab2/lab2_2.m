N = 800;
K = 600;
nu = 0;
o = 1;

W = o * randn(N, K);
RW = zeros(N, K);
RW(1, :) = W(1, :);

for n = 2:N
    RW(n, :) = RW(n-1, :) + W(n, :);
end

figure;
plot(RW);
xlabel('Отсчет времени (n)');
ylabel('Значение случайного блуждания');
title('Реализации случайных блужданий');

pairs1 = [10, 9; 50, 49; 100, 99; 200, 199];
pairs2 = [50, 40; 100, 90; 200, 190];
colors = ['r', 'g', 'b', 'm'];

figure;

subplot(1, 2, 1);
hold on;
for i = 1:size(pairs1, 1)
    ni = pairs1(i, 1);
    nj = pairs1(i, 2);
    scatter(RW(ni, :), RW(nj, :), 5, colors(i), 'filled');
end
xlabel('e[n_i]');
ylabel('e[n_j]');
title('Диаграммы рассеяния');
legend('(10, 9)', '(50, 49)', '(100, 99)', '(200, 199)');

subplot(1, 2, 2);
hold on;
for i = 1:size(pairs2, 1)
    ni = pairs2(i, 1);
    nj = pairs2(i, 2);
    scatter(RW(ni, :), RW(nj, :), 5, colors(i), 'filled');
end
xlabel('e[n_i]');
ylabel('e[n_j]');
title('Диаграммы рассеяния ');
legend('(50, 40)', '(100, 90)', '(200, 190)');

r_e_hat = zeros(N-1, 1);

for n = 2:N
    r_e_hat(n-1) = mean(RW(n, :) .* RW(n-1, :));
end

r_e_theoretical = (1:N-1)';

figure;
hold on;
plot(r_e_hat, 'b-', 'LineWidth', 2);
plot(r_e_theoretical, 'r--', 'LineWidth', 2);
xlabel('n');
ylabel('r_e(n, n-1)');
title('Автокорреляция случайного блуждания');
legend('Выборочная АКФ', 'Теоретическая АКФ');
grid on;
