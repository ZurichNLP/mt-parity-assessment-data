require(gtools)
require(dplyr)

results = read.table('results.aggregated.tsv', sep = '\t', header = TRUE)
N=150
N_total = N*9 # number of error categories

get_percentage <- function(vector, n=N, digits=1) {
  percentage = vector/N*100
  rounded = lapply(percentage, round, digits)
  formatted = lapply(rounded, format, nsmall = digits)
  return(unlist(formatted))
}

get_significance <- function(errors_system1, errors_system2, error_category) {
  n = ifelse(error_category=='Total', N_total, N)
  x = c(errors_system1, errors_system2)
  y = c(n - errors_system1, n - errors_system2)
  contingency_table = cbind(x, y)
  analysis = fisher.test(contingency_table, alternative='two.sided')
  return(
    stars.pval(analysis$p.value)
  )
}

# add significance (Fisher's exact test)
results$a_b = mapply(get_significance, results$human_a, results$human_b, results$Error.Category)
results$a_mt = mapply(get_significance, results$human_a, results$mt, results$Error.Category)
results$b_mt = mapply(get_significance, results$human_b, results$mt, results$Error.Category)

# only keep error category, percentage, significance
results = select(results, Error.Category, human_a, human_b, mt, a_b, a_mt, b_mt)
write.csv(results, file='results.final.csv', row.names=F)
