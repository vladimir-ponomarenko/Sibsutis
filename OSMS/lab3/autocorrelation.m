a1 = [0.03, 0.02, 1, 4.2, -2, 1.5, 0];
b1 = [0.009, 400, -20, 1006, 10, 0.001, 20];

correlatA1 = zeros(1, length(a1));
corr_norma = zeros(1, length(a1));
corr_normb = zeros(1, length(a1));



for i = 1:length(a1)
    data_new = circshift(a1, i - 1);
    correlatA1(i) = sum(a1 .* data_new);
    sum_a = sum(a1 .* a1);
    sum_b = sum(data_new .* data_new);
    corr_norma(i) = correlatA1(i) / sqrt(sum_a * sum_b);
end

correlatB1 = zeros(1, length(b1));

for i = 1:length(b1)
    data_new1 = circshift(b1, i - 1);
    correlatB1(i) = sum(b1 .* data_new1);
    sum_ab = sum(b1 .* b1);
    sum_bb = sum(data_new1 .* data_new1);
    corr_normb(i) = correlatB1(i) / sqrt(sum_ab * sum_bb);
end

disp(corr_norma)
disp(corr_normb)

%disp(correlatA1)
%disp(correlatB1)

t1 = 0:length(a1) - 1;
t2 = 0:length(b1) - 1;

figure;

subplot(3, 1, 1);
plot(t1, corr_norma);
title('Автокорреляция a1');

subplot(3, 1, 2);
plot(t2, corr_normb);
title('Автокорреляция b1');
