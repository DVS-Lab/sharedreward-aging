# Install libraries if necessary
# install.packages("here")
# install.packages("dplyr")
# install.packages("ggplot2")

# Load necessary libraries
library(here)
library(dplyr)
library(ggplot2)

# Read the data
data <- read.csv(here("code", "fdmean_conf.csv"))

# Create a new column to categorize the length of 'sub'
data <- data %>%
  mutate(sub_length = ifelse(nchar(as.character(sub)) == 3, "SRNDNA", "RF1"))

# Function to determine if a value is an outlier
is_outlier <- function(x) {
  Q1 <- quantile(x, 0.25, na.rm = TRUE)
  Q3 <- quantile(x, 0.75, na.rm = TRUE)
  IQR <- Q3 - Q1
  lower_bound <- Q1 - 1.5 * IQR
  upper_bound <- Q3 + 1.5 * IQR
  return(ifelse(x < lower_bound | x > upper_bound, "outlier", "non-outlier"))
}

# Apply the function to add a new column indicating outliers
data <- data %>%
  group_by(sub_length) %>%
  mutate(outlier_status = is_outlier(fd_mean)) %>%
  ungroup()

# Plotting the box plots with enhanced aesthetics, individual data points, and marked outliers
ggplot(data, aes(x = sub_length, y = fd_mean)) +
  geom_boxplot(outlier.shape = NA, fill = "lightblue", color = "darkblue", alpha = 0.5) + # Adjust boxplot aesthetics without marking outliers separately
  geom_jitter(width = 0.2, size = 1.5, alpha = 0.7, aes(color = outlier_status)) + # Add individual data points, coloring outliers differently
  scale_color_manual(values = c("non-outlier" = "darkblue", "outlier" = "red")) + # Set colors for outliers and non-outliers
  labs(title = "fd_mean by Project for each run of each sub",
       x = "",
       y = "average fd_mean",
       color = "Outlier Status") +
  theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"), # Center and bold the title
    axis.title.x = element_text(face = "bold"),
    axis.title.y = element_text(face = "bold"),
    axis.text = element_text(size = 12)
  )
