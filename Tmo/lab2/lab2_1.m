N = 800;
K = 600;
mu = 16;
sigma = 4;
nu = 0;
o = 1;
l1 = 8;
l2 = 80;

Xi = mu + sigma * randn(N, K);

mu_n = mean(Xi, 2);

mu_k = mean(Xi, 1);

figure;
hold on;
plot(mu_n, 'b-', 'LineWidth', 2);
plot(mu_k, 'r--', 'LineWidth', 1);
xlabel('Отсчет времени (n)');
ylabel('Среднее значение');
title('Белый гауссовский шум - Среднее по ансамблю и среднее по времени');
legend('Среднее по ансамблю', 'Среднее по времени');
grid on;

pairs = [10, 11; 50, 55; 200, 250];
figure;
for i = 1:size(pairs, 1)
    ni = pairs(i, 1);
    nj = pairs(i, 2);
    subplot(1, 3, i);
    scatter(Xi(ni, :), Xi(nj, :), '.');
    xlabel(['e[', num2str(ni), ']']);
    ylabel(['e[', num2str(nj), ']']);
    title(['Диаграмма рассеяния (n_i=', num2str(ni), ', n_j=', num2str(nj), ')']);
    r = corrcoef(Xi(ni, :), Xi(nj, :));
    disp(['Выборочная корреляция (n_i=', num2str(ni), ', n_j=', num2str(nj), '): ', num2str(r(1, 2))]);
end

W = o * randn(N, K);
RW = zeros(N, K);
RW(1, :) = W(1, :);
for n = 2:N
    RW(n, :) = RW(n-1, :) + W(n, :);
end

theoretical_mu_RW = (1:N) * nu;

disp(['Теоретическое среднее значение случайных блужданий для каждого n: ', num2str(theoretical_mu_RW)]);

mu_n_RW = mean(RW, 2);

figure;
hold on;
plot(mu_n_RW, 'b-', 'LineWidth', 2);
plot(theoretical_mu_RW, 'r--', 'LineWidth', 2);
xlabel('Отсчет времени (n)');
ylabel('Среднее значение');
title('Случайные блуждания - Среднее по ансамблю');
legend('Среднее по ансамблю (эмпирическое)', 'Среднее по ансамблю (теоретическое)');
grid on;
