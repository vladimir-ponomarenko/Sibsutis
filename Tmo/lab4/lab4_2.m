function main
  I = 18;
  J = 33;

  calculateAndDisplay(I, J);
end

function calculateAndDisplay(I, J)
  vector_column = generateRandomVector(I, 1);
  vector_row = generateRandomVector(1, J);

  result_matrix = vector_column * vector_row;

  mean_value = mean(result_matrix(:));
  variance = var(result_matrix(:));

  fprintf('Размерность вектора-столбца: %d\n', I);
  fprintf('Размерность вектора-строки: %d\n', J);
  fprintf('Среднее значение матрицы: %f\n', mean_value);
  fprintf('Дисперсия матрицы: %f\n', variance);
end

function randomVector = generateRandomVector(rows, cols)
  randomVector = (rand(rows, cols) - 0.5) * 10; 
end 
