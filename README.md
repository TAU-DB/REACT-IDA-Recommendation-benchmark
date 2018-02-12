# REACT-IDA
Benchmark dataset and source code for Modern Interactive Data Analysis (IDA) recommender systems.

## The Problem: Modern IDA Recommendations
Modern Interactive Data Analysis (IDA) platforms, such as Kibana,
Splunk, and Tableau, are gradually replacing traditional OLAP/SQL
tools, as they allow for easy-to-use data exploration,
visualization, and mining, even for users lacking SQL and
programming skills. Nevertheless, data analysis is still a difficult
task, especially for non-expert users.

There are two major challenges stems from the modern, often web-based analysis platforms:
1. IDA platforms facilitate composite analysis processes,
interweaving actions of  multiple types (filtering,
aggregation, pattern mining, visualization, etc.) while providing a
simplified syntax. 

2. In common IDA business environments, users (even of the same
department) often examine different datasets, for different
purposes. 

## REACT: Next Step Suggestions for Modern Data Analysis Platforms
REACT is a recommender system designated
for modern IDA platforms, which particularly tackles the new
challenges that they pose. Given the specific context of the user
(e.g., the analysis actions of all types performed thus far by the user,
the results obtained, the properties of the data set at hand, etc.),
REACT processes and adapts previous experience of other analysts
working with the same or related datasets, in order to present the
user with personalized next-step suggestions.

## Benchmark Dataset: Real-world IDA logs.
To our knowledge, there are no publicly available repositories of analysis actions performed on modern IDA platforms.
This benchmark dataset contains real-world analysis log in the domain of cyber security.

**IMPORTANT: Our work is currently submitted to publication. Meanwhile, We only provide the benchmark and source code upon requiest.**
Please email us at **amitsome@mail.tau.ac.il** for inqueries and data requests. 

###Data Collection
We recruited 56 analysts, specializing in the domain of cyber-security (via dedicated forums, network security firms, and volunteer senior students from the Israeli National Cyber-Security Program), and asked them to analyze 4 different datasets using a prototype web-based analysis platform that we developed.
Each dataset, provided by the "Honeynet Project", contains between 350 to 13K rows of raw network logs that may reveal a distinct security event, e.g. malware communication hidden in network traffic, hacking activity inside a local network, an IP range/port scan, etc. (there is no connection between the tuples of different datasets).
The analysts were asked to perform as many analysis actions as required to reveal the details of the underlying security event of each dataset.

 

