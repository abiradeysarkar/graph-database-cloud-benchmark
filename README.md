# Graph Database Cloud Benchmark

A reproducible benchmark suite for comparing managed graph database platforms using the same dataset, workloads, and benchmark methodology.

The goal is to provide an honest comparison of performance characteristics rather than optimize the benchmark for a particular database.

## Current Status

The CognoDB Cloud baseline implementation is complete for:

- Dataset preparation and validation
- Dataset ingestion
- Schema and index setup
- 1-hop traversal
- 2-hop traversal
- 3-hop traversal
- Point lookup
- Indexed/filtered lookup
- Aggregation
- 10-client concurrent mixed read/write workload

Comparison benchmarks for additional graph database platforms are still in progress.

---

## Benchmark Dataset

### Source

SNAP Pokec social network dataset:

https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz

The benchmark uses a reproducible subset of the original Pokec relationship dataset.

### Benchmark dataset

| Property | Value |
|---|---:|
| Source relationships processed | 30,622,564 |
| Benchmark relationships | 200,000 |
| Unique users | 297,688 |
| Duplicate edges | 0 |
| Self-loops | 0 |
| Dataset SHA-256 | `2576637e63e091d0d490df194ad76501021303707db3b1db9795cc6174876805` |

The processed dataset is generated from the original SNAP source using the dataset preparation script.

Validation confirms:

- 200,000 relationships
- 297,688 unique users
- No duplicate edges
- No self-loops

---

## CognoDB Cloud Environment

CognoDB Cloud was configured using the free C0 instance.

The benchmark uses the official Neo4j Python driver over the CognoDB Bolt+S connection.

Connection details are provided through environment variables and are never committed to the repository.

### Authentication

Required environment variables:

```text
COGNODB_URI
COGNODB_USERNAME
COGNODB_PASSWORD

------------------------------------------------------------------------------------------------------------
CognoDB Results
Data Ingestion

The dataset was loaded using batched Cypher writes.
User ingestion

| Metric          |      Result |
| --------------- | ----------: |
| Users           |     297,688 |
| Batch size      |       1,000 |
| Batches         |         298 |
| Wall-clock time | 501.660 sec |
| Users/sec       |      593.41 |


Relationship ingestion
| Metric            |      Result |
| ----------------- | ----------: |
| Relationships     |     200,000 |
| Batch size        |       1,000 |
| Batches           |         200 |
| Wall-clock time   | 341.424 sec |
| Relationships/sec |      585.78 |

1-Hop Traversal
| Metric              |     Result |
| ------------------- | ---------: |
| Valid start nodes   |    167,834 |
| Warm-up iterations  |         20 |
| Measured iterations |        100 |
| p50                 | 303.017 ms |
| p95                 | 353.701 ms |
| Mean                | 288.736 ms |
| Min                 | 253.916 ms |
| Max                 | 366.547 ms |

Result:
results/cognodb/1hop.json

2-Hop Traversal
| Metric              |     Result |
| ------------------- | ---------: |
| Valid start nodes   |    167,834 |
| Warm-up iterations  |         20 |
| Measured iterations |        100 |
| p50                 | 304.805 ms |
| p95                 | 352.409 ms |
| Mean                | 295.378 ms |
| Min                 | 260.293 ms |
| Max                 | 356.187 ms |

Result:
results/cognodb/2hop.json

3-Hop Traversal
| Metric              |     Result |
| ------------------- | ---------: |
| Valid start nodes   |    167,834 |
| Warm-up iterations  |         20 |
| Measured iterations |        100 |
| p50                 | 288.285 ms |
| p95                 | 350.247 ms |
| Mean                | 289.228 ms |
| Min                 | 258.857 ms |
| Max                 | 361.281 ms |

Result:
results/cognodb/3hop.json

Point Lookup
| Metric              |     Result |
| ------------------- | ---------: |
| Warm-up iterations  |         20 |
| Measured iterations |        100 |
| p50                 | 265.583 ms |
| p95                 | 329.244 ms |
| Mean                | 274.944 ms |
| Min                 | 242.233 ms |
| Max                 | 355.781 ms |

Result:
results/cognodb/point_lookup.json

Indexed / Filtered Lookup

The filtered lookup uses the indexed User.bucket property.
| Metric              |     Result |
| ------------------- | ---------: |
| Warm-up iterations  |         20 |
| Measured iterations |        100 |
| p50                 | 305.934 ms |
| p95                 | 347.427 ms |
| Mean                | 297.601 ms |
| Min                 | 267.503 ms |
| Max                 | 378.053 ms |

Result:

results/cognodb/filtered_lookup.json

Aggregation

The aggregation workload performs a group-by style query over the graph.
| Metric              |       Result |
| ------------------- | -----------: |
| Warm-up iterations  |           20 |
| Measured iterations |          100 |
| p50                 |   865.015 ms |
| p95                 |   968.709 ms |
| Mean                |   867.214 ms |
| Min                 |   765.474 ms |
| Max                 | 1,056.212 ms |

Mixed Read/Write Workload

The initial concurrency test uses:

10 concurrent clients
80% reads
20% writes
60-second target workload duration

Temporary BENCHMARK_WRITE relationships are used for the write workload and cleaned up after the test.

10-client result
| Metric           |       Result |
| ---------------- | -----------: |
| Clients          |           10 |
| Elapsed time     |   67.840 sec |
| Total operations |          602 |
| Reads            |          475 |
| Writes           |          127 |
| Errors           |            0 |
| Throughput       | 8.87 ops/sec |
| p50 latency      |   266.934 ms |
| p95 latency      | 6,188.333 ms |
| Mean latency     | 1,102.663 ms |

Result:

results/cognodb/mixed_workload_10_clients.json 