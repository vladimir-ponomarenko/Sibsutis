f1 = 12;
f2 = 12 + 4;
f3 = 12 * 2 + 1;

t = (0:99) / 100;

s1 = cos(2 * pi * f1 * t);
s2 = cos(2 * pi * f2 * t);
s3 = cos(2 * pi * f3 * t);

a = 4 * s1 + 4 * s2 + s3;
b = 2 * s1 + s2 + 2 * s3;

corr1 = sum(a .* b);
corr2 = sum(s1 .* a);
corr3 = sum(s1 .* b);
sum_a = sum(a .* a);
sum_b = sum(b .* b);
sum_s1 = sum(s1 .* s1);
corr_norm1 = corr1 / sqrt(sum_a * sum_b);
corr_norm2 = corr2 / sqrt(sum_s1 * sum_a);
corr_norm3 = corr3 / sqrt(sum_s1 * sum_b);

fprintf("Корреляция a и b: %f\n", corr1);
fprintf("Корреляция s1 и a: %f\n", corr2);
fprintf("Корреляция s1 и b: %f\n", corr3);
fprintf("Нормализованная корреляция a и b: %f\n", corr_norm1);
fprintf("Нормализованная корреляция s1 и a: %f\n", corr_norm2);
fprintf("Нормализованная корреляция s1 и b: %f\n", corr_norm3);

a1 = [0.3, 0.2, -0.1, 4.2, -2, 1.5, 0];
b1 = [0.3, 4, -2.2, 1.6, 0.1, 0.1, 0.2];
t1 = 0:length(a1) - 1;
correlat = zeros(1, length(a1));

for i = 1:length(a1)
    data_new = circshift(b1, i - 1);
    correlat(i) = sum(a1 .* data_new);
end

[~, max_corr_idx] = max(correlat);
b_max = circshift(b1, max_corr_idx - 1);

figure;

subplot(3, 1, 1);
plot(t1, a1);
title('Сигнал a');

subplot(3, 1, 2);
plot(t1, b1);
title('Сигнал b');

subplot(3, 1, 3);
plot(t1, b_max);
title('Сигнал b с максимальной корреляцией');

figure;
plot(t1, correlat);
title('Корреляция при сдвиге');
xlabel('Сдвиг');
ylabel('Корреляция');

disp(correlat)