f = @(x) (1./x) .* log(abs(1-x));

x = linspace(-2, 2.99, 1000);

figure;
subplot(3,1,1);
plot(x, f(x));
title('График функции f(x) = (1/x) * ln|1-x|');
xlabel('x');
ylabel('f(x)');

syms x_sym;
f_sym = (1/x_sym) * log(abs(1-x_sym));
df_sym = diff(f_sym, x_sym);
df = matlabFunction(df_sym);

subplot(3,1,2);
plot(x, df(x));
title('График производной f''(x)');
xlabel('x');
ylabel('f''(x)');

int_f = zeros(size(x));
for i = 1:length(x)
    int_f(i) = integral(f, 0, x(i));
end

subplot(3,1,3);
plot(x, int_f); 
title('График интеграла \int_0^x f(y) dy');
xlabel('x');
ylabel('\int_0^x f(y) dy');

a = 1; 
b = 0.5; 

figure;
plot(x, f(x));
hold on;
plot(x, a*x + b);
title('Графическое решение уравнения');
xlabel('x');
ylabel('y');
legend('f(x)', 'a*x + b');

fun = @(x) f(x) - a*x - b;
x_sol = fzero(fun, 0.5);
fprintf('Решение уравнения x = %f\n', x_sol);

F = @(x, y) acos(x) + asin(y);

[X,Y] = meshgrid(-1:0.05:1, -1:0.05:1);
Z = F(X, Y);

figure;
surf(X, Y, Z);
title('График функции F(x, y) = arccos(x) + arcsin(y)');
xlabel('x');
ylabel('y');
zlabel('F(x, y)');
colorbar;
shading interp;
