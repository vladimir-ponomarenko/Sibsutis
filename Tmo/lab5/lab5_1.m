L = 15; 
T = zeros(L, L);

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

% Проверка матрицы на стохастичность
isStochastic = stochastic(T);
fprintf('Матрица стохастична: %s\n', mat2str(isStochastic));

% Проверка на эргодичность
epsilon = 1e-5;
isErgodic = ergodic(T, epsilon);
fprintf('Цепь Маркова эргодична: %s\n', mat2str(isErgodic));

function result = stochastic(matrix)
  if size(matrix, 1) ~= size(matrix, 2)
    result = false; 
    return;
  end
  result = all(matrix(:) >= 0) && all(abs(sum(matrix, 2) - 1) < 1e-10);
end

function result = ergodic(matrix, epsilon)
  if ~stochastic(matrix)
    result = false;
    return;
  end

  % Проверка на эргодичность
  for i = 1:size(matrix, 1)
    initialState = zeros(1, size(matrix, 1));
    initialState(i) = 1;
    finalState = initialState * (matrix^200);
    if any(finalState < epsilon)
      result = false;
      return;
    end
  end

  result = true;
end
