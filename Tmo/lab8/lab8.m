x = 5; % Среднее время обслуживания
ro = 0.1:0.05:0.95; % Коэффициент загрузки
Cb2 = [0, 1, 10, 20, 30:10:100]; % Нормированная дисперсия времени обслуживания

Nq_MG1 = zeros(length(Cb2), length(ro));
N_MG1 = zeros(length(Cb2), length(ro));
W_MG1 = zeros(length(Cb2), length(ro));
T_MG1 = zeros(length(Cb2), length(ro));

Nq_MD1 = zeros(1, length(ro));
N_MD1 = zeros(1, length(ro));
W_MD1 = zeros(1, length(ro));
T_MD1 = zeros(1, length(ro));

Nq_MM1 = zeros(1, length(ro));
N_MM1 = zeros(1, length(ro));
W_MM1 = zeros(1, length(ro));
T_MM1 = zeros(1, length(ro));

for i = 1:length(Cb2)
    Nq_MG1(i,:) = (ro.^2 .* (1 + Cb2(i))) ./ (2 * (1 - ro));
    N_MG1(i,:) = ro + Nq_MG1(i,:);
    W_MG1(i,:) = (ro .* x .* (1 + Cb2(i))) ./ (2 * (1 - ro));
    T_MG1(i,:) = x + W_MG1(i,:);
end

% M/D/1
Nq_MD1 = ro.^2 ./ (2 * (1 - ro));
N_MD1 = ro + Nq_MD1;
W_MD1 = (ro .* x) ./ (2 * (1 - ro));
T_MD1 = (x .* (2 - ro)) ./ (2 * (1 - ro));

% M/M/1
Nq_MM1 = ro.^2 ./ (1 - ro);
N_MM1 = ro ./ (1 - ro);
W_MM1 = (ro .* x) ./ (1 - ro);
T_MM1 = x ./ (1 - ro);

figure;

subplot(2,2,1);
hold on;
for i = 1:length(Cb2)
    plot(ro, Nq_MG1(i,:), 'DisplayName', ['M/G/1, Cb2 = ', num2str(Cb2(i))]);
end
plot(ro, Nq_MD1, 'DisplayName', 'M/D/1');
plot(ro, Nq_MM1, 'DisplayName', 'M/M/1');
xlabel('Коэффициент загрузки (ро)');
ylabel('Средняя длина очереди (Nq)');
legend('show');
title('Зависимость средней длины очереди от коэффициента загрузки');

subplot(2,2,2);
hold on;
for i = 1:length(Cb2)
    plot(ro, N_MG1(i,:), 'DisplayName', ['M/G/1, Cb2 = ', num2str(Cb2(i))]);
end
plot(ro, N_MD1, 'DisplayName', 'M/D/1');
plot(ro, N_MM1, 'DisplayName', 'M/M/1');
xlabel('Коэффициент загрузки (ро)');
ylabel('Среднее число заявок в СМО (N)');
legend('show');
title('Зависимость среднего числа заявок в СМО от коэффициента загрузки');

subplot(2,2,3);
hold on;
for i = 1:length(Cb2)
    plot(ro, W_MG1(i,:), 'DisplayName', ['M/G/1, Cb2 = ', num2str(Cb2(i))]);
end
plot(ro, W_MD1, 'DisplayName', 'M/D/1');
plot(ro, W_MM1, 'DisplayName', 'M/M/1');
xlabel('Коэффициент загрузки (ро)');
ylabel('Среднее время ожидания (W)');
legend('show');
title('Зависимость среднего времени ожидания от коэффициента загрузки');

subplot(2,2,4);
hold on;
for i = 1:length(Cb2)
    plot(ro, T_MG1(i,:), 'DisplayName', ['M/G/1, Cb2 = ', num2str(Cb2(i))]);
end
plot(ro, T_MD1, 'DisplayName', 'M/D/1');
plot(ro, T_MM1, 'DisplayName', 'M/M/1');
xlabel('Коэффициент загрузки (ро)');
ylabel('Среднее время пребывания (T)');
legend('show');
title('Зависимость среднего времени пребывания от коэффициента загрузки');

hold off;
