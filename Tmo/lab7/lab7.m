% 2.
lambda = 2;  % Интенсивность входного потока
mu = 3;      % Интенсивность обслуживания

if lambda >= mu
    error('Система нестационарна. Выберите λ < μ.');
end

% 3. 
% Для входного потока:
E_tau = 1 / lambda;     
D_tau = 1 / lambda^2;   

% Для времени обслуживания:
E_nu = 1 / mu;         
D_nu = 1 / mu^2;        

fprintf('Интенсивность входного потока (λ): %f\n', lambda);
fprintf('Интенсивность обслуживания (μ): %f\n\n', mu);

fprintf('Входной поток (показательное распределение):\n');
fprintf('  Математитическое ожидание: %f\n', E_tau);
fprintf('  Дисперсия: %f\n\n', D_tau);

fprintf('Время обслуживания (показательное распределение):\n');
fprintf('  Математическое ожидание: %f\n', E_nu);
fprintf('  Дисперсия: %f\n\n', D_nu);

% 4. Равномерное распределение
syms a b
eqns = [(a + b)/2 == E_tau, (b - a)^2/12 == D_tau];
sol = solve(eqns, [a, b], 'Real', true);
a_unif = double(sol.a(sol.b > sol.a)); 
b_unif = double(sol.b(sol.b > sol.a));

% 5.
E_unif = (a_unif + b_unif) / 2; 
D_unif = (b_unif - a_unif)^2 / 12; 

fprintf('Равномерное распределение:\n');
fprintf('  Математическое ожидание: %f\n', E_unif);
fprintf('  Дисперсия: %f\n\n', D_unif);

% 6. 
N = 10000;

% 7. 
tau_n = exprnd(E_tau, 1, N); 
nu_n = exprnd(E_nu, 1, N);    
tau1_n = a_unif + (b_unif - a_unif) * rand(1, N);
nu1_n = a_unif + (b_unif - a_unif) * rand(1, N);

% 8. 
[arrivals_MM1, departures_MM1, queue_length_MM1, queue_dist_MM1, ...
    ro_MM1, L_MM1, Wq_MM1, W_MM1] = simulate_queue(tau_n, nu_n);

[arrivals_MG1, departures_MG1, queue_length_MG1, queue_dist_MG1, ...
    ro_MG1, L_MG1, Wq_MG1, W_MG1] = simulate_queue(tau_n, nu1_n);

[arrivals_GM1, departures_GM1, queue_length_GM1, queue_dist_GM1, ...
    ro_GM1, L_GM1, Wq_GM1, W_GM1] = simulate_queue(tau1_n, nu_n);

[arrivals_GG1, departures_GG1, queue_length_GG1, queue_dist_GG1, ...
    ro_GG1, L_GG1, Wq_GG1, W_GG1] = simulate_queue(tau1_n, nu1_n);

figure;
subplot(2,2,1);
plot(arrivals_MM1, 1:N, 'b-', departures_MM1, 1:N, 'r-');
xlabel('Время');
ylabel('Число заявок');
title('M/M/1: Поступление/Уход заявок');
legend('Поступление', 'Уход');

subplot(2,2,2);
plot(arrivals_MG1, 1:N, 'b-', departures_MG1, 1:N, 'r-');
xlabel('Время');
ylabel('Число заявок');
title('M/G/1: Поступление/Уход заявок');
legend('Поступление', 'Уход');

subplot(2,2,3);
plot(arrivals_GM1, 1:N, 'b-', departures_GM1, 1:N, 'r-');
xlabel('Время');
ylabel('Число заявок');
title('G/M/1: Поступление/Уход заявок');
legend('Поступление', 'Уход');

subplot(2,2,4);
plot(arrivals_GG1, 1:N, 'b-', departures_GG1, 1:N, 'r-');
xlabel('Время');
ylabel('Число заявок');
title('G/G/1: Поступление/Уход заявок');
legend('Поступление', 'Уход');

figure;
subplot(2,2,1);
plot(queue_length_MM1);
xlabel('Время');
ylabel('Длина очереди');
title('M/M/1: Длина очереди');

subplot(2,2,2);
plot(queue_length_MG1);
xlabel('Время');
ylabel('Длина очереди');
title('M/G/1: Длина очереди');

subplot(2,2,3);
plot(queue_length_GM1);
xlabel('Время');
ylabel('Длина очереди');
title('G/M/1: Длина очереди');

subplot(2,2,4);
plot(queue_length_GG1);
xlabel('Время');
ylabel('Длина очереди');
title('G/G/1: Длина очереди');

figure;
subplot(2,2,1);
bar(0:length(queue_dist_MM1)-1, queue_dist_MM1);
xlabel('Длина очереди');
ylabel('Частота');
title('M/M/1: Распределение длины очереди');

subplot(2,2,2);
bar(0:length(queue_dist_MG1)-1, queue_dist_MG1);
xlabel('Длина очереди');
ylabel('Частота');
title('M/G/1: Распределение длины очереди');

subplot(2,2,3);
bar(0:length(queue_dist_GM1)-1, queue_dist_GM1);
xlabel('Длина очереди');
ylabel('Частота');
title('G/M/1: Распределение длины очереди');

subplot(2,2,4);
bar(0:length(queue_dist_GG1)-1, queue_dist_GG1);
xlabel('Длина очереди');
ylabel('Частота');
title('G/G/1: Распределение длины очереди');

fprintf('\nСтатистические характеристики СМО:\n');
fprintf('-----------------------------------\n');
fprintf('M/M/1:  ρ = %.4f, L = %.4f, Wq = %.4f, W = %.4f\n', ...
    ro_MM1, L_MM1, Wq_MM1, W_MM1);
fprintf('M/G/1:  ρ = %.4f, L = %.4f, Wq = %.4f, W = %.4f\n', ...
    ro_MG1, L_MG1, Wq_MG1, W_MG1);
fprintf('G/M/1:  ρ = %.4f, L = %.4f, Wq = %.4f, W = %.4f\n', ...
    ro_GM1, L_GM1, Wq_GM1, W_GM1);
fprintf('G/G/1:  ρ = %.4f, L = %.4f, Wq = %.4f, W = %.4f\n', ...
    ro_GG1, L_GG1, Wq_GG1, W_GG1);

function [arrivals, departures, queue_length, queue_dist, ro, L, Wq, W] = ...
    simulate_queue(tau, nu)
    
    N = length(tau);
    arrivals = cumsum(tau);            % Моменты поступления заявок
    departures = zeros(1, N);          % Моменты ухода заявок
    queue_length = zeros(1, N);       % Длина очереди
    
    departures(1) = arrivals(1) + nu(1);
    
    for i = 2:N
        if arrivals(i) < departures(i-1)
            queue_length(i) = queue_length(i-1) + 1; 
        else
            queue_length(i) = max(0, queue_length(i-1) - 1);
        end
        departures(i) = max(arrivals(i), departures(i-1)) + nu(i);
    end
    
    queue_dist = hist(queue_length, 0:max(queue_length)); 
    
    ro = sum(nu) / departures(end);              % Коэффициент загрузки
    L = sum(queue_length) / N;                   % Среднее число заявок в СМО
    Wq = sum(queue_length .* tau) / sum(tau);   % Среднее время пребывания в очереди
    W = sum((departures - arrivals)) / N;          % Среднее время пребывания в СМО
end
