% Функция для генерации выборочных значений
function x = generate_random_values(N)
  z = rand(1, N); 
  % Метод обратных функций
  x = 1 ./ sqrt(1 - z);
end

% Функция плотности распределения
function y = pdf_func(x)
  y = 2 ./ (x.^3);
end

% Функция функции распределения
function y = cdf_func(x)
  y = 1 - 1 ./ (x.^2);
end

% Функция для генерации выборочных значений дискретной случайной величины
function x = generate_discrete_random_values(N)
  k = 0:100;
  p = 2.^(-k-1); 
  
  % Кумулятивная функция распределения (cdf)
  cdf = cumsum(p); 

  u = rand(1, N);

  x = arrayfun(@(val) find(cdf >= val, 1) - 1, u);
end

N1 = 50;
N2 = 200;
N3 = 1000;
sample1_discrete = generate_discrete_random_values(N1);
sample2_discrete = generate_discrete_random_values(N2);
sample3_discrete = generate_discrete_random_values(N3);

N1 = 50;
N2 = 200;
N3 = 1000;
sample1 = generate_random_values(N1);
sample2 = generate_random_values(N2);
sample3 = generate_random_values(N3);

mean1 = mean(sample1);
mean2 = mean(sample2);
mean3 = mean(sample3);

var1 = var(sample1);
var2 = var(sample2);
var3 = var(sample3);

std1 = std(sample1);
std2 = std(sample2);
std3 = std(sample3);

fprintf('Выборка N = %d:\n', N1);
fprintf('  Среднее: %f\n', mean1);
fprintf('  Дисперсия: %f\n', var1);
fprintf('  СКО: %f\n\n', std1);

fprintf('Выборка N = %d:\n', N2);
fprintf('  Среднее: %f\n', mean2);
fprintf('  Дисперсия: %f\n', var2);
fprintf('  СКО: %f\n\n', std2);

fprintf('Выборка N = %d:\n', N3);
fprintf('  Среднее: %f\n', mean3);
fprintf('  Дисперсия: %f\n', var3);
fprintf('  СКО: %f\n\n', std3);


mean1_discrete = mean(sample1_discrete);
mean2_discrete = mean(sample2_discrete);
mean3_discrete = mean(sample3_discrete);

var1_discrete = var(sample1_discrete);
var2_discrete = var(sample2_discrete);
var3_discrete = var(sample3_discrete);

std1_discrete = std(sample1_discrete);
std2_discrete = std(sample2_discrete);
std3_discrete = std(sample3_discrete);

fprintf('ДИСКРЕТНАЯ СЛУЧАЙНАЯ ВЕЛИЧИНА\n');
fprintf('Выборка N = %d:\n', N1);
fprintf('  Среднее: %f\n', mean1_discrete);
fprintf('  Дисперсия: %f\n', var1_discrete);
fprintf('  СКО: %f\n\n', std1_discrete);

fprintf('Выборка N = %d:\n', N2);
fprintf('  Среднее: %f\n', mean2_discrete);
fprintf('  Дисперсия: %f\n', var2_discrete);
fprintf('  СКО: %f\n\n', std2_discrete);

fprintf('Выборка N = %d:\n', N3);
fprintf('  Среднее: %f\n', mean3_discrete);
fprintf('  Дисперсия: %f\n', var3_discrete);
fprintf('  СКО: %f\n\n', std3_discrete);

% Интервальные оценки среднего и дисперсии
alphas = [0.1, 0.05, 0.01];

% Таблица для хранения результатов ДИСКРЕТНОЙ СЛУЧАЙНОЙ ВЕЛИЧИНЫ
results_discrete = table();

for i = 1:length(alphas)
  alpha = alphas(i);
  
  t_score1 = tinv(1-alpha/2, N1-1);
  ci_mean1_discrete = mean1_discrete + [-1, 1] * t_score1 * std1_discrete/sqrt(N1); 

  t_score2 = tinv(1-alpha/2, N2-1);
  ci_mean2_discrete = mean2_discrete + [-1, 1] * t_score2 * std2_discrete/sqrt(N2);

  t_score3 = tinv(1-alpha/2, N3-1);
  ci_mean3_discrete = mean3_discrete + [-1, 1] * t_score3 * std3_discrete/sqrt(N3); 
  
  ci_var1_discrete = (N1-1)*var1_discrete ./ chi2inv([alpha/2, 1-alpha/2], N1-1);
  ci_var2_discrete = (N2-1)*var2_discrete ./ chi2inv([alpha/2, 1-alpha/2], N2-1);
  ci_var3_discrete = (N3-1)*var3_discrete ./ chi2inv([alpha/2, 1-alpha/2], N3-1);

  results_discrete = [results_discrete; {N1, alpha, ci_mean1_discrete, ci_var1_discrete}; ...
                     {N2, alpha, ci_mean2_discrete, ci_var2_discrete}; ...
                     {N3, alpha, ci_mean3_discrete, ci_var3_discrete}];
end

results_discrete.Properties.VariableNames = {'N', 'Alpha', 'Доверительный_интервал_среднего', 'Доверительный_интервал_дисперсии'};

disp("ДИСКРЕТНАЯ СЛУЧАЙНАЯ ВЕЛИЧИНА")
disp(results_discrete)

results = table();

for i = 1:length(alphas)
  alpha = alphas(i);
  
  t_score1 = tinv(1-alpha/2, N1-1);
  ci_mean1 = mean1 + [-1, 1] * t_score1 * std1/sqrt(N1); 

  t_score2 = tinv(1-alpha/2, N2-1);
  ci_mean2 = mean2 + [-1, 1] * t_score2 * std2/sqrt(N2);

  t_score3 = tinv(1-alpha/2, N3-1);
  ci_mean3 = mean3 + [-1, 1] * t_score3 * std3/sqrt(N3); 
  
  ci_var1 = (N1-1)*var1 ./ chi2inv([alpha/2, 1-alpha/2], N1-1);
  ci_var2 = (N2-1)*var2 ./ chi2inv([alpha/2, 1-alpha/2], N2-1);
  ci_var3 = (N3-1)*var3 ./ chi2inv([alpha/2, 1-alpha/2], N3-1);

  results = [results; {N1, alpha, ci_mean1, ci_var1}; ...
                     {N2, alpha, ci_mean2, ci_var2}; ...
                     {N3, alpha, ci_mean3, ci_var3}];
end

results.Properties.VariableNames = {'N', 'Alpha', 'Доверительный_интервал_среднего', 'Доверительный_интервал_дисперсии'};

disp("НЕПРЕРЫВНАЯ СЛУЧАЙНАЯ ВЕЛИЧИНА")
disp(results)

figure;

subplot(3,1,1);
k1 = ceil(1 + 3.2 * log(N1));
histogram(sample1, k1, 'Normalization', 'pdf');
hold on;
x_range = linspace(1, max(sample1), 100);
plot(x_range, pdf_func(x_range), 'r-', 'LineWidth', 2);
title(['Гистограмма и плотность распределения для N = ', num2str(N1)]);
hold off;

subplot(3,1,2);
k2 = ceil(1 + 3.2 * log(N2)); 
histogram(sample2, k2, 'Normalization', 'pdf');
hold on;
x_range = linspace(1, max(sample2), 100);
plot(x_range, pdf_func(x_range), 'r-', 'LineWidth', 2);
title(['Гистограмма и плотность распределения для N = ', num2str(N2)]);
hold off;

subplot(3,1,3);
k3 = ceil(1 + 3.2 * log(N3)); 
histogram(sample3, k3, 'Normalization', 'pdf');
hold on;
x_range = linspace(1, max(sample3), 100);
plot(x_range, pdf_func(x_range), 'r-', 'LineWidth', 2);
title(['Гистограмма и плотность распределения для N = ', num2str(N3)]);
hold off;

sgtitle('Гистограммы и плотности распределения выборок');

figure;
x_range = linspace(1, 10, 100); 
plot(x_range, pdf_func(x_range), 'b-', 'LineWidth', 2);
hold on;
plot(x_range, cdf_func(x_range), 'r-', 'LineWidth', 2);
title('Плотность и функция распределения');
xlabel('x');
ylabel('f(x) / F(x)');
legend('Плотность распределения', 'Функция распределения');


figure;

subplot(3,1,1);
k1 = ceil(1 + 3.2 * log(N1));

[unique_vals, ~, idx] = unique(sample1_discrete);
counts = accumarray(idx, 1);

bar(unique_vals, counts/N1, 'hist');
hold on;

k_theoretical = 0:max(unique_vals); 
p_theoretical = 2.^(-k_theoretical-1);
stem(k_theoretical, p_theoretical, 'r-', 'LineWidth', 2);

title(['Гистограмма и закон распределения для N = ', num2str(N1)]);
xlabel('k');
ylabel('P(X=k)');
legend('Эмпирическое распределение', 'Теоретическое распределение');
hold off;

subplot(3,1,2);
k2 = ceil(1 + 3.2 * log(N2));

[unique_vals, ~, idx] = unique(sample2_discrete);
counts = accumarray(idx, 1);

bar(unique_vals, counts/N2, 'hist'); 
hold on;

k_theoretical = 0:max(unique_vals); 
p_theoretical = 2.^(-k_theoretical-1);
stem(k_theoretical, p_theoretical, 'r-', 'LineWidth', 2);

title(['Гистограмма и закон распределения для N = ', num2str(N2)]);
xlabel('k');
ylabel('P(X=k)');
legend('Эмпирическое распределение', 'Теоретическое распределение');
hold off;

subplot(3,1,3);
k3 = ceil(1 + 3.2 * log(N3));

[unique_vals, ~, idx] = unique(sample3_discrete);
counts = accumarray(idx, 1);

bar(unique_vals, counts/N3, 'hist'); 
hold on;

k_theoretical = 0:max(unique_vals); 
p_theoretical = 2.^(-k_theoretical-1);
stem(k_theoretical, p_theoretical, 'r-', 'LineWidth', 2);

title(['Гистограмма и закон распределения для N = ', num2str(N3)]);
xlabel('k');
ylabel('P(X=k)');
legend('Эмпирическое распределение', 'Теоретическое распределение');
hold off;

sgtitle('Гистограммы и законы распределения для дискретной случайной величины');


figure;
k = 0:20;
p = 2.^(-k-1); 
cdf = cumsum(p);

stairs(k, [cdf(1), diff(cdf)], 'b-', 'LineWidth', 2);
hold on;
stem(k, p, 'r-', 'LineWidth', 2);

title('Закон распределения и функция распределения (дискретная СВ)');
xlabel('k');
ylabel('P(X=k) / F(k)');
legend('Функция распределения', 'Закон распределения');
xlim([-0.5, 20.5]); 
grid on;
