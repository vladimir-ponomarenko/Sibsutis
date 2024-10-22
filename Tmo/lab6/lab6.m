% 2. 
lambda = 2;  % Интенсивность входного потока
mu = 3;      % Интенсивность обслуживания

if lambda >= mu
    error('Система нестационарна. Выберите λ < μ.');
end

% 3.
% Для входного потока:
E_tau = 1 / lambda;     % Математическое ожидание времени между поступлениями
D_tau = 1 / lambda^2;   % Дисперсия времени между поступлениями

% Для времени обслуживания:
E_nu = 1 / mu;         % Математическое ожидание времени обслуживания
D_nu = 1 / mu^2;        % Дисперсия времени обслуживания

fprintf('Интенсивность входного потока (λ): %f\n', lambda);
fprintf('Интенсивность обслуживания (μ): %f\n\n', mu);

fprintf('Входной поток (показательное распределение):\n');
fprintf('  Математическое ожидание: %f\n', E_tau);
fprintf('  Дисперсия: %f\n\n', D_tau);

fprintf('Время обслуживания (показательное распределение):\n');
fprintf('  Математическое ожидание: %f\n', E_nu);
fprintf('  Дисперсия: %f\n\n', D_nu);

% 4.
syms a b
eqns = [(a + b)/2 == E_tau, (b - a)^2/12 == D_tau];
sol = solve(eqns, [a, b], 'Real', true);
a_unif = double(sol.a(sol.b > sol.a)); 
b_unif = double(sol.b(sol.b > sol.a));

% 5.
E_unif = (a_unif + b_unif) / 2; % Математическое ожидание
D_unif = (b_unif - a_unif)^2 / 12; % Дисперсия

fprintf('Равномерное распределение:\n');
fprintf('  Математическое ожидание: %f\n', E_unif);
fprintf('  Дисперсия: %f\n\n', D_unif);

% 6.
N = 10000;

% 7.
tau_n = exprnd(E_tau, 1, N); 
nu_n = exprnd(E_nu, 1, N);    

% 8.
tau1_n = a_unif + (b_unif - a_unif) * rand(1, N);
nu1_n = a_unif + (b_unif - a_unif) * rand(1, N);

% 9. 
% Для M/M/1:
M_tau = mean(tau_n);       
D_tau = var(tau_n);        
M_nu = mean(nu_n);         
D_nu = var(nu_n);          

% Для G/G/1:
M_tau1 = mean(tau1_n);     
D_tau1 = var(tau1_n);       
M_nu1 = mean(nu1_n);        
D_nu1 = var(nu1_n);         

fprintf('\nСтатистические характеристики выборок:\n');
fprintf('-----------------------------------------\n');
fprintf('M/M/1:\n');
fprintf('  tau_n:  Среднее = %f, Дисперсия = %f\n', M_tau, D_tau);
fprintf('  nu_n:   Среднее = %f, Дисперсия = %f\n', M_nu, D_nu);

fprintf('\nG/G/1 (равномерное распределение):\n');
fprintf('  tau1_n: Среднее = %f, Дисперсия = %f\n', M_tau1, D_tau1);
fprintf('  nu1_n:  Среднее = %f, Дисперсия = %f\n', M_nu1, D_nu1);

% 10.
fprintf('\nСравнение аналитических и статистических характеристик:\n');
fprintf('-------------------------------------------------------------\n');
fprintf('M/M/1 (tau_n):   | Аналитическое: E = %.4f, D = %.4f\n', E_tau, D_tau);
fprintf('                | Статистическое: E = %.4f, D = %.4f\n', M_tau, D_tau);
fprintf('M/M/1 (nu_n):    | Аналитическое: E = %.4f, D = %.4f\n', E_nu, D_nu);
fprintf('                | Статистическое: E = %.4f, D = %.4f\n', M_nu, D_nu);

fprintf('G/G/1 (tau1_n): | Аналитическое: E = %.4f, D = %.4f\n', E_unif, D_unif);
fprintf('                | Статистическое: E = %.4f, D = %.4f\n', M_tau1, D_tau1);
fprintf('G/G/1 (nu1_n):  | Аналитическое: E = %.4f, D = %.4f\n', E_unif, D_unif);
fprintf('                | Статистическое: E = %.4f, D = %.4f\n', M_nu1, D_nu1);

% 11.
fprintf('\nСравнение статистических характеристик распределений:\n');
fprintf('---------------------------------------------------------\n');
fprintf('tau_n (показательное) / tau1_n (равномерное):\n');
fprintf('  Средние:     %.4f / %.4f\n', M_tau, M_tau1);
fprintf('  Дисперсии:  %.4f / %.4f\n', D_tau, D_tau1);

fprintf('\nnu_n (показательное) / nu1_n (равномерное):\n');
fprintf('  Средние:     %.4f / %.4f\n', M_nu, M_nu1);
fprintf('  Дисперсии:  %.4f / %.4f\n', D_nu, D_nu1);
