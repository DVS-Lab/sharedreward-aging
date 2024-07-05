# Load necessary libraries
library(dplyr)
library(ggplot2)

# Read the combined CSV file
data <- read.csv('/ZPOOL/data/projects/sharedreward-aging/code/combined_logs-edited.csv')

# Function to calculate SEM
calculate_sem <- function(x) {
  return(sd(x, na.rm = TRUE) / sqrt(length(na.omit(x))))
}

# Filter the data and calculate average responses and SEM for both trait conditions
avg_responses_trait_0 <- data %>%
  filter(trait == 0) %>%
  group_by(partner) %>%
  summarise(average_response = mean(response, na.rm = TRUE),
            sem = calculate_sem(response)) %>%
  mutate(trait = "Win")

avg_responses_trait_1 <- data %>%
  filter(trait == 1) %>%
  group_by(partner) %>%
  summarise(average_response = mean(response, na.rm = TRUE),
            sem = calculate_sem(response)) %>%
  mutate(trait = "Loss")

# Combine both results into one DataFrame
combined_avg_responses <- bind_rows(avg_responses_trait_0, avg_responses_trait_1)

# Display the average responses in a bar plot with SEM error bars
ggplot(combined_avg_responses, aes(x = factor(partner), y = average_response, fill = trait)) +
  geom_bar(stat = "identity", position = position_dodge(0.9)) +
  geom_errorbar(aes(ymin = average_response - sem, ymax = average_response + sem),
                position = position_dodge(0.9), width = 0.25) +
  labs(title = "Average Responses for Each Partner Condition by Trait",
       x = "Partner Condition",
       y = "Average Response",
       fill = "Trait") +
  scale_x_discrete(labels = c("1" = "Computer", "2" = "Stranger", "3" = "Friend")) +
  theme_minimal()
