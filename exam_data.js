/**
 * exam_data.js
 * -------------------------------------------------------
 * DP-800 SQL AI Engineer — Sample Questions
 *
 * To create a different exam, duplicate this file and edit
 * the examConfig and examQuestions objects. Keep the same
 * structure so the UI can consume any swap-in data file.
 *
 * Question types supported:
 *   "multiple-choice"  — requires an options array
 *   "exact-word"       — requires correctAnswer string,
 *                        optional caseSensitive boolean
 * -------------------------------------------------------
 */

const examConfig = {
  title: "DP-800 SQL AI Engineer",
  subtitle: "Certification Review Tool",
  description:
    "Practice questions covering Azure Synapse, Delta Lake, T-SQL, and data engineering concepts.",
  passingScore: 70,
  shuffleQuestions: true,
  shuffleOptions: true,
};

const examQuestions = [
  {
    id: 1,
    type: "multiple-choice",
    question:
      "In Azure Synapse Analytics, which type of SQL pool allows you to query data stored in Azure Data Lake Storage or Azure Blob Storage using T-SQL on demand, without provisioning any compute resources?",
    options: [
      "Dedicated SQL Pool",
      "Serverless SQL Pool",
      "Apache Spark Pool",
      "Data Explorer Pool",
    ],
    correctAnswer: "Serverless SQL Pool",
    explanation:
      "Serverless SQL Pool in Azure Synapse Analytics enables you to query data directly from your data lake using familiar T-SQL syntax without needing to provision or manage any infrastructure. You are billed based on the amount of data processed per query. Dedicated SQL Pool, by contrast, requires pre-provisioned DWU (Data Warehouse Units) and incurs costs regardless of usage.",
  },
  {
    id: 2,
    type: "exact-word",
    question:
      "What T-SQL window function assigns a unique sequential integer to each row within a partition of a result set, starting from 1, without gaps even when there are duplicate values?",
    correctAnswer: "ROW_NUMBER",
    caseSensitive: false,
    explanation:
      "ROW_NUMBER() is a ranking window function that assigns a sequential integer to each row within a partition, starting at 1. Unlike RANK() and DENSE_RANK(), ROW_NUMBER() does not account for ties — it always increments by 1, which means tied rows receive different numbers arbitrarily. This is commonly used for pagination and deduplication.",
  },
  {
    id: 3,
    type: "multiple-choice",
    question:
      "Which columnar file format is recommended by Microsoft for optimal query performance in Azure Synapse serverless SQL pools, due to its support for column pruning, predicate pushdown, and column-level statistics?",
    options: [
      "CSV (Comma-Separated Values)",
      "JSON (JavaScript Object Notation)",
      "Parquet",
      "Avro",
    ],
    correctAnswer: "Parquet",
    explanation:
      "Parquet is an open-source, columnar storage format designed for efficient data storage and retrieval. In Synapse serverless SQL pools, Parquet files benefit from column pruning (only reading needed columns), predicate pushdown (filtering at the storage layer), and column-level statistics for query optimization. This makes Parquet significantly faster and more cost-effective than row-oriented formats like CSV or JSON for analytical queries.",
  },
  {
    id: 4,
    type: "multiple-choice",
    question:
      "In Azure Databricks, what critical capability does Delta Lake add on top of standard Parquet file storage?",
    options: [
      "Built-in natural language processing",
      "ACID transaction support, schema enforcement, and time travel",
      "Automatic GPU acceleration for all queries",
      "Integrated web hosting for data visualizations",
    ],
    correctAnswer:
      "ACID transaction support, schema enforcement, and time travel",
    explanation:
      "Delta Lake is an open-source storage layer that enhances data lake reliability by adding ACID (Atomicity, Consistency, Isolation, Durability) transactions on top of Parquet files. It provides schema enforcement to prevent corrupt data from being written, schema evolution for safe schema changes, and time travel (versioning) that allows you to query previous snapshots of your data or roll back changes.",
  },
  {
    id: 5,
    type: "exact-word",
    question:
      "What T-SQL statement creates a named, persistent virtual table in the database that stores the defining SELECT query but does not store the underlying data physically?",
    correctAnswer: "CREATE VIEW",
    caseSensitive: false,
    explanation:
      "CREATE VIEW defines a virtual table based on a SELECT statement. The view definition is stored in the database catalog, but the data itself is not materialized — it is fetched from the underlying base tables each time the view is queried. Views are useful for simplifying complex joins, restricting column-level access for security, and providing a stable interface when underlying table schemas change.",
  },
];
