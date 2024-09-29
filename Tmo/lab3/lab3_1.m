% Задание значений элементов матрицы переходов
p11 = 2; p12 = 5; p13 = 3; p14 = 4;
p21 = 8; p22 = 5; p23 = 4; p24 = 2;
p31 = 5; p32 = 4; p33 = 3; p34 = 2;
p41 = 1; p42 = 5; p43 = 4; p44 = 4;

P = [p11 p12 p13 p14;
     p21 p22 p23 p24;
     p31 p32 p33 p34;
     p41 p42 p43 p44];
P = P ./ sum(P,2);

% Создание цепи Маркова MC
MC = dtmc(P);

% Задание имен состояний
MC.StateNames = ["Healthy", "Unwell", "Sick", "Very sick"]; 

% Вывод матрицы переходов
disp("Матрица переходов MC.P:")
disp(MC.P)

% Проверка суммы строк матрицы
disp("Сумма строк матрицы MC.P:")
disp(sum(MC.P, 2)) 

% Построение графа с раскраской ребер по вероятностям
figure 
graphplot(MC,'ColorEdges',true)

% Создание кумулятивной матрицы переходов P_cum
P_cum = cumsum(MC.P, 2);

% Моделирование поведения цепи Маркова
numIterations = 200;
Z = zeros(1, numIterations);
Z(1) = 1;

for t = 1:numIterations-1
    r = rand();
    k = find(r > P_cum(Z(t), :), 1, 'last');
    if isempty(k)
        Z(t+1) = 1; 
    else
        Z(t+1) = k + 1; 
    end
end

disp("Траектория состояний цепи Маркова:")
disp(Z)

% Построение графика траектории состояний
figure
plot(1:numIterations, Z);
xlabel('Итерация');
ylabel('Состояние цепи Маркова');
title('Траектория состояний цепи Маркова');

% Моделирование для 1000 итераций
numIterations = 1000;
Z_1000 = zeros(1, numIterations);
Z_1000(1) = 1; 

for t = 1:numIterations-1
    r = rand();
    k = find(r > P_cum(Z_1000(t), :), 1, 'last');
    if isempty(k)
        Z_1000(t+1) = 1; 
    else
        Z_1000(t+1) = k + 1; 
    end
end

% Построение графика для 1000 итераций
figure 
plot(1:1000, Z_1000);
xlabel('Итерация');
ylabel('Состояние цепи Маркова');
title('Траектория состояний цепи Маркова (1000 итераций)');

% disp("Траектория состояний цепи Маркова (1000 итераций):")
% disp(Z_1000)

% Моделирование для 10000 итераций
numIterations = 10000;
Z_10000 = zeros(1, numIterations);
Z_10000(1) = 1; 

for t = 1:numIterations-1
    r = rand();
    k = find(r > P_cum(Z_10000(t), :), 1, 'last');
    if isempty(k)
        Z_10000(t+1) = 1; 
    else
        Z_10000(t+1) = k + 1; 
    end
end

% Построение графика для 10000 итераций
figure 
plot(1:10000, Z_10000);
xlabel('Итерация');
ylabel('Состояние цепи Маркова');
title('Траектория состояний цепи Маркова (10000 итераций)');

% Вывод результата моделирования для 10000 итераций
% disp("Траектория состояний цепи Маркова (10000 итераций):")
% disp(Z_10000)


% Расчет и обработка оценок цепи Маркова
iterations = [200, 1000, 10000];
Z_all = {Z, Z_1000, Z_10000};

for i = 1:length(iterations)
    numIterations = iterations(i);
    Z_current = Z_all{i};

    % Расчет оценки матрицы переходов
    P_obs = zeros(4, 4);
    for t = 1:numIterations-1
        P_obs(Z_current(t), Z_current(t+1)) = P_obs(Z_current(t), Z_current(t+1)) + 1;
    end
    P_obs = P_obs ./ sum(P_obs, 2);

    disp(['Матрица переходов (', num2str(numIterations), ' итераций):'])
    disp(P_obs)

    % Проверка суммы строк матрицы
    disp(['Сумма строк матрицы (', num2str(numIterations), ' итераций):'])
    disp(sum(P_obs, 2))

    % Построение графа
    figure
    MC_obs = dtmc(P_obs);
    MC_obs.StateNames = ["Healthy", "Unwell", "Sick", "Very sick"]; 
    graphplot(MC_obs, 'ColorEdges', true);
    title(['Граф цепи Маркова (', num2str(numIterations), ' итераций)']);
end

% Моделирование на основе оцененной матрицы (200 итераций)
numIterations = 200;
Z_200_obs = zeros(1, numIterations);
Z_200_obs(1) = 1; 

P_cum_obs = cumsum(P_obs, 2); % Кумулятивная матрица для P_obs (200 итераций)

for t = 1:numIterations-1
    r = rand();
    k = find(r > P_cum_obs(Z_200_obs(t), :), 1, 'last');
    if isempty(k)
        Z_200_obs(t+1) = 1; 
    else
        Z_200_obs(t+1) = k + 1; 
    end
end

% Построение графика для симуляции на основе оцененной матрицы
figure
subplot(1, 2, 1);
plot(1:numIterations, Z_200_obs);
xlabel('Итерация');
ylabel('Состояние цепи Маркова');
title('На основе оцененной матрицы (200)');

% Построение графика для исходной симуляции (200 итераций)
subplot(1, 2, 2);
plot(1:numIterations, Z);
xlabel('Итерация');
ylabel('Состояние цепи Маркова');
title('Исходная симуляция (200)');

% Вывод кумулятивной матрицы
disp("Кумулятивная матрица переходов:")
disp(P_cum)
