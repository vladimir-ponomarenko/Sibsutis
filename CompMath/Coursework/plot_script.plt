set title 'Number of Infected Over Time'
set xlabel 'Number of Infected'
set ylabel 'Days'
set term x11
plot 'data_plot.txt' with lines
pause -1 'Press any key to exit'
