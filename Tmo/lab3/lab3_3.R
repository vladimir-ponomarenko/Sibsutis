install.packages("markovchain")

library(markovchain)

P <- matrix(c(2, 5, 3, 4,
              8, 5, 4, 2,
              5, 4, 3, 2,
              1, 5, 4, 4), 
            nrow = 4, byrow = TRUE)
P <- P / rowSums(P)

mc <- new("markovchain", states = c("Healthy", "Unwell", "Sick", "Very sick"),
          transitionMatrix = P)

mc
 
initialState <- "Healthy"
nIterations <- 200
simulatedStates <- rmarkovchain(n = nIterations, object = mc, t0 = initialState)
print(simulatedStates)

