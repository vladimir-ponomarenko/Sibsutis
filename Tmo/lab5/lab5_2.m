T = zeros(15,15);
T(1, 2) = 0.4;  T(1, 5) = 0.3;  T(1, 8) = 0.3;
T(2, 1) = 0.2;  T(2, 3) = 0.5;  T(2, 6) = 0.3;
T(3, 2) = 0.3;  T(3, 4) = 0.4;  T(3, 7) = 0.3;
T(4, 3) = 0.2;  T(4, 5) = 0.5;  T(4, 9) = 0.3;
T(5, 4) = 0.3;  T(5, 6) = 0.4;  T(5, 10) = 0.3;
T(6, 5) = 0.2;  T(6, 7) = 0.5;  T(6, 11) = 0.3;
T(7, 6) = 0.3;  T(7, 8) = 0.4;  T(7, 12) = 0.3;
T(8, 7) = 0.2;  T(8, 9) = 0.5;  T(8, 13) = 0.3;
T(9, 8) = 0.3;  T(9, 10) = 0.4;  T(9, 14) = 0.3;
T(10, 9) = 0.2; T(10, 11) = 0.5; T(10, 15) = 0.3;
T(11, 10) = 0.3; T(11, 12) = 0.4; T(11, 1) = 0.3; 
T(12, 11) = 0.2; T(12, 13) = 0.5; T(12, 2) = 0.3;
T(13, 12) = 0.3; T(13, 14) = 0.4; T(13, 3) = 0.3;
T(14, 13) = 0.2; T(14, 15) = 0.5; T(14, 4) = 0.3;
T(15, 14) = 0.3; T(15, 1) = 0.4; T(15, 5) = 0.3; 

N = 100;   % Длина траектории
s = 1;      % Начальное состояние
epsilon = 1e-6; % Точность

trajectory = MarkovTrajectory(T, N, s);

figure;
plot(0:N, trajectory);
xlabel('Шаг времени');
ylabel('Номер узла');
title('Траектория движения пакета');

L = size(T, 1);
P_stay = zeros(L, L);
P_first = zeros(L, L);
M_shortest = zeros(L, L);
M_expected = zeros(L, L);
D = zeros(L, L);

for i = 1:L
  for j = 1:L
    m = 1;
    P_first(i, j) = T(i, j);
    while P_first(i, j) < epsilon && m < 1000
      m = m + 1;
      temp = 1;
      for q = 1:m-1
        temp = temp * (1 - T(i, j));
      end
      P_first(i, j) = T(i, j) * temp;
    end
    M_shortest(i, j) = m;
    
    m = 1;
    P_stay(i, j, m) = T(i, j);
    M_expected(i, j) = m * P_first(i, j);
    D(i, j) = m^2 * P_first(i, j) - M_expected(i, j)^2;
    while m < 1000
      m = m + 1;
      temp = T^m;
      P_stay(i, j, m) = temp(i, j);
      M_expected(i, j) = M_expected(i, j) + m * P_first(i, j);
      D(i, j) = D(i, j) + m^2 * P_first(i, j) - M_expected(i, j)^2;
    end
  end
end

% Вероятности пребывания пакета в узлах
figure;
hold on;
for i = 1:L
  plot(1:L, P_stay(i, :, 10), '-o');
end
xlabel('Номер узла');
ylabel('Вероятность пребывания');
title('Вероятности пребывания пакета в узлах');
legend(cellstr(num2str((1:L)', 'Узел %d')), 'Location', 'eastoutside');

% Вероятности первого перехода
figure;
hold on;
for i = 1:L
  plot(1:L, P_first(i, :), '-o');
end
xlabel('Номер узла');
ylabel('Вероятность первого перехода');
title('Вероятности первого перехода пакета');
legend(cellstr(num2str((1:L)', 'Из узла %d')), 'Location', 'eastoutside');

% Длины кратчайших путей
figure;
imagesc(M_shortest);
colorbar;
xlabel('Номер узла');
ylabel('Номер узла');
title('Длины кратчайших путей');

% Математические ожидания длин путей
figure;
imagesc(M_expected);
colorbar;
xlabel('Номер узла');
ylabel('Номер узла');
title('Математические ожидания длин путей');

figure;
imagesc(D);
colorbar;
xlabel('Номер узла');
ylabel('Номер узла');
title('Дисперсии длин путей');

hold off;

% Расчет траектории движения пакета
function E = MarkovTrajectory(P, N, s)
  E = zeros(1, N+1);
  E(1) = s;
  S = size(P, 1) - 1;
  
  for i = 0:S
    for j = 1:S
      P(i+1, j+1) = P(i+1, j+1) + P(i+1, j);
    end
  end
  
  for i = 2:N+1
    r = rand();
    E(i) = S+1; 
    for j = 1:S
      if r < P(E(i-1), j)
        E(i) = j;
        break;
      end
    end
  end
end
