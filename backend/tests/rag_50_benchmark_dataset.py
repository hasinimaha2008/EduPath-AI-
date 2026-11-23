"""
Comprehensive 50-Question Information Retrieval & RAG Benchmark Dataset for EduPath AI.
Spans 8 Core Computer Science Domains:
1. Database Management Systems (DBMS)
2. Operating Systems (OS)
3. Computer Networks (CN)
4. Data Structures & Algorithms (DSA)
5. Artificial Intelligence & Machine Learning (AI/ML)
6. Cloud Computing & Distributed Systems
7. Cybersecurity & Applied Cryptography
8. Software Architecture & System Design
"""

RAG_BENCHMARK_50_QUESTIONS = [
    # --- 1. Database Management Systems (DBMS) ---
    {
        "id": "RAG-Q01",
        "domain": "DBMS",
        "query": "How do ACID properties guarantee transaction integrity in relational databases?",
        "expected_keywords": ["atomicity", "consistency", "isolation", "durability", "transaction", "rollback", "commit"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q02",
        "domain": "DBMS",
        "query": "What is the structural difference between B-Tree and B+ Tree indexing for range queries?",
        "expected_keywords": ["b+ tree", "leaf", "range", "pointers", "index", "disk", "node"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q03",
        "domain": "DBMS",
        "query": "Explain database normalization from 1NF through BCNF and how it eliminates anomalies.",
        "expected_keywords": ["normalization", "1nf", "2nf", "3nf", "bcnf", "functional dependency", "anomaly"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q04",
        "domain": "DBMS",
        "query": "How does Two-Phase Locking (2PL) prevent conflict serializability violations?",
        "expected_keywords": ["two-phase", "2pl", "locking", "growing", "shrinking", "serializability", "concurrency"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q05",
        "domain": "DBMS",
        "query": "What is Write-Ahead Logging (WAL) and how does it support crash recovery in ARIES?",
        "expected_keywords": ["write-ahead", "wal", "recovery", "aries", "log", "redo", "undo", "crash"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q06",
        "domain": "DBMS",
        "query": "How do foreign key constraints enforce referential integrity across relational tables?",
        "expected_keywords": ["foreign key", "referential", "integrity", "primary key", "cascade", "constraint"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q07",
        "domain": "DBMS",
        "query": "How do SQL window functions differ from standard GROUP BY aggregations?",
        "expected_keywords": ["window", "partition by", "group by", "over", "rank", "aggregation", "rows"],
        "min_relevance_threshold": 0.6
    },

    # --- 2. Operating Systems (OS) ---
    {
        "id": "RAG-Q08",
        "domain": "OS",
        "query": "How does virtual memory paging translate logical addresses to physical addresses using TLB?",
        "expected_keywords": ["virtual memory", "paging", "tlb", "translation", "page table", "physical", "frame"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q09",
        "domain": "OS",
        "query": "What happens during a process context switch and how does the OS save state in PCB?",
        "expected_keywords": ["context switch", "pcb", "registers", "state", "process", "kernel", "overhead"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q10",
        "domain": "OS",
        "query": "What are the four necessary Coffman conditions required for a deadlock to occur?",
        "expected_keywords": ["coffman", "deadlock", "mutual exclusion", "hold and wait", "no preemption", "circular wait"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q11",
        "domain": "OS",
        "query": "How do counting semaphores and binary mutexes prevent race conditions in critical sections?",
        "expected_keywords": ["semaphore", "mutex", "race condition", "critical section", "wait", "signal", "atomic"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q12",
        "domain": "OS",
        "query": "How does the Completely Fair Scheduler (CFS) allocate CPU time using red-black trees?",
        "expected_keywords": ["cfs", "scheduler", "vruntime", "red-black", "cpu", "fair", "time slice"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q13",
        "domain": "OS",
        "query": "What triggers a page fault interrupt and how does the operating system handle it?",
        "expected_keywords": ["page fault", "interrupt", "swap", "disk", "handler", "frame", "memory"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q14",
        "domain": "OS",
        "query": "Explain user mode vs kernel mode transitions when executing system calls via trap interrupts.",
        "expected_keywords": ["user mode", "kernel mode", "system call", "trap", "interrupt", "privilege", "ring"],
        "min_relevance_threshold": 0.6
    },

    # --- 3. Computer Networks (CN) ---
    {
        "id": "RAG-Q15",
        "domain": "CN",
        "query": "How does the TCP three-way handshake establish a reliable connection between client and server?",
        "expected_keywords": ["tcp", "three-way", "syn", "ack", "handshake", "sequence", "connection"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q16",
        "domain": "CN",
        "query": "Compare TCP and UDP in terms of reliability, ordering, flow control, and transmission overhead.",
        "expected_keywords": ["tcp", "udp", "reliable", "connectionless", "flow control", "overhead", "datagram"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q17",
        "domain": "CN",
        "query": "How does DNS resolution resolve domain names to IP addresses through root and authoritative servers?",
        "expected_keywords": ["dns", "resolution", "root", "tld", "authoritative", "cache", "ip address"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q18",
        "domain": "CN",
        "query": "How does CIDR subnetting divide IPv4 address spaces to prevent routing table explosion?",
        "expected_keywords": ["cidr", "subnet", "ipv4", "mask", "prefix", "routing", "network"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q19",
        "domain": "CN",
        "query": "How does HTTP/2 multiplexing eliminate head-of-line blocking present in HTTP/1.1?",
        "expected_keywords": ["http/2", "multiplexing", "head-of-line", "streams", "binary", "framing", "latency"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q20",
        "domain": "CN",
        "query": "Explain how the TLS 1.3 cryptographic handshake establishes an encrypted session.",
        "expected_keywords": ["tls", "handshake", "cryptographic", "certificate", "cipher", "session", "encryption"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q21",
        "domain": "CN",
        "query": "What is the difference between distance-vector and link-state routing algorithms?",
        "expected_keywords": ["distance-vector", "link-state", "dijkstra", "bellman-ford", "routing", "topology"],
        "min_relevance_threshold": 0.6
    },

    # --- 4. Data Structures & Algorithms (DSA) ---
    {
        "id": "RAG-Q22",
        "domain": "DSA",
        "query": "How do hash tables resolve key collisions using separate chaining vs open addressing?",
        "expected_keywords": ["hash table", "collision", "chaining", "open addressing", "probing", "load factor"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q23",
        "domain": "DSA",
        "query": "What balancing rules govern Red-Black trees to maintain O(log n) search height guarantees?",
        "expected_keywords": ["red-black", "balance", "rotation", "height", "log n", "tree", "root"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q24",
        "domain": "DSA",
        "query": "How does Dijkstra algorithm find single-source shortest paths using a priority queue min-heap?",
        "expected_keywords": ["dijkstra", "shortest path", "priority queue", "heap", "relaxation", "graph", "distance"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q25",
        "domain": "DSA",
        "query": "What properties define dynamic programming and differentiate memoization from tabulation?",
        "expected_keywords": ["dynamic programming", "memoization", "tabulation", "overlapping", "optimal substructure"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q26",
        "domain": "DSA",
        "query": "Compare average and worst-case asymptotic bounds for QuickSort and MergeSort algorithms.",
        "expected_keywords": ["quicksort", "mergesort", "asymptotic", "complexity", "o(n log n)", "o(n^2)", "divide"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q27",
        "domain": "DSA",
        "query": "How does Kahn algorithm perform topological sorting on a directed acyclic graph (DAG)?",
        "expected_keywords": ["kahn", "topological", "dag", "indegree", "directed", "queue", "cycle"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q28",
        "domain": "DSA",
        "query": "How does a Trie prefix tree store strings to allow O(m) prefix searches and autocomplete?",
        "expected_keywords": ["trie", "prefix", "strings", "nodes", "autocomplete", "children", "search"],
        "min_relevance_threshold": 0.6
    },

    # --- 5. Artificial Intelligence & Machine Learning ---
    {
        "id": "RAG-Q29",
        "domain": "AI/ML",
        "query": "How does stochastic gradient descent update weights to minimize loss functions during training?",
        "expected_keywords": ["gradient descent", "weights", "loss", "learning rate", "stochastic", "optimization"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q30",
        "domain": "AI/ML",
        "query": "Explain the difference between L1 Lasso and L2 Ridge regularization for preventing overfitting.",
        "expected_keywords": ["l1", "l2", "lasso", "ridge", "regularization", "overfitting", "sparsity", "penalty"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q31",
        "domain": "AI/ML",
        "query": "How does multi-head self-attention allow Transformers to process token relationships in parallel?",
        "expected_keywords": ["multi-head", "self-attention", "transformer", "query", "key", "value", "parallel"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q32",
        "domain": "AI/ML",
        "query": "How do dense vector embeddings capture semantic similarity using cosine distance?",
        "expected_keywords": ["embeddings", "vector", "semantic", "cosine", "similarity", "dimensions", "dense"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q33",
        "domain": "AI/ML",
        "query": "What is the trade-off between Precision and Recall and how is it summarized by the F1-Score?",
        "expected_keywords": ["precision", "recall", "f1-score", "trade-off", "false positive", "false negative"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q34",
        "domain": "AI/ML",
        "query": "How does backpropagation compute gradients using the calculus chain rule across neural network layers?",
        "expected_keywords": ["backpropagation", "chain rule", "gradient", "layers", "derivatives", "neural network"],
        "min_relevance_threshold": 0.6
    },

    # --- 6. Cloud Computing & Distributed Systems ---
    {
        "id": "RAG-Q35",
        "domain": "Distributed Systems",
        "query": "Explain the CAP theorem and the fundamental trade-off between consistency and availability.",
        "expected_keywords": ["cap theorem", "consistency", "availability", "partition tolerance", "distributed"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q36",
        "domain": "Cloud",
        "query": "What architectural benefits and trade-offs exist between microservices and modular monoliths?",
        "expected_keywords": ["microservices", "monolith", "decoupling", "network latency", "deployment", "services"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q37",
        "domain": "Cloud",
        "query": "How do Docker images utilize union file system layers and copy-on-write storage?",
        "expected_keywords": ["docker", "layers", "union", "copy-on-write", "image", "container", "cache"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q38",
        "domain": "Cloud",
        "query": "How does Kubernetes manage pod lifecycles, health checks (liveness/readiness), and deployments?",
        "expected_keywords": ["kubernetes", "pod", "liveness", "readiness", "deployment", "replica", "controller"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q39",
        "domain": "Cloud",
        "query": "How does Horizontal Pod Autoscaling (HPA) scale container replicas based on CPU/memory utilization?",
        "expected_keywords": ["hpa", "autoscaling", "replicas", "cpu", "utilization", "metrics", "scaling"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q40",
        "domain": "Distributed Systems",
        "query": "How does the Raft consensus algorithm elect leaders and maintain replicated state logs?",
        "expected_keywords": ["raft", "consensus", "leader election", "log replication", "heartbeat", "quorum"],
        "min_relevance_threshold": 0.6
    },

    # --- 7. Cybersecurity & Applied Cryptography ---
    {
        "id": "RAG-Q41",
        "domain": "Security",
        "query": "What is the structural difference between symmetric AES and asymmetric RSA cryptography?",
        "expected_keywords": ["symmetric", "asymmetric", "aes", "rsa", "public key", "private key", "encryption"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q42",
        "domain": "Security",
        "query": "How do parameterized prepared statements defend applications against SQL Injection attacks?",
        "expected_keywords": ["sql injection", "parameterized", "prepared statements", "sanitization", "query"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q43",
        "domain": "Security",
        "query": "Explain Cross-Site Scripting (XSS) types and how Content Security Policy (CSP) mitigates them.",
        "expected_keywords": ["xss", "cross-site scripting", "csp", "content security policy", "stored", "reflected"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q44",
        "domain": "Security",
        "query": "How does a JSON Web Token (JWT) structure its header, payload, and cryptographic signature?",
        "expected_keywords": ["jwt", "token", "header", "payload", "signature", "hmac", "rsa", "claims"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q45",
        "domain": "Security",
        "query": "How does Public Key Infrastructure (PKI) use Certificate Authorities to verify digital trust?",
        "expected_keywords": ["pki", "certificate authority", "ca", "digital certificate", "chain of trust", "x.509"],
        "min_relevance_threshold": 0.6
    },

    # --- 8. Software Architecture & System Design ---
    {
        "id": "RAG-Q46",
        "domain": "System Design",
        "query": "Explain the Single Responsibility and Dependency Inversion principles in SOLID architecture.",
        "expected_keywords": ["solid", "single responsibility", "dependency inversion", "interfaces", "decoupling"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q47",
        "domain": "System Design",
        "query": "Compare Cache-Aside (Lazy Loading) and Write-Through caching patterns for read-heavy workloads.",
        "expected_keywords": ["cache-aside", "write-through", "caching", "redis", "invalidation", "stale", "ttl"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q48",
        "domain": "System Design",
        "query": "How does the Token Bucket rate limiting algorithm regulate bursty client traffic?",
        "expected_keywords": ["rate limiting", "token bucket", "burst", "refill", "throttling", "capacity", "api"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q49",
        "domain": "System Design",
        "query": "How do asynchronous message brokers like Kafka or RabbitMQ decouple microservices?",
        "expected_keywords": ["message broker", "kafka", "rabbitmq", "asynchronous", "queue", "producer", "consumer"],
        "min_relevance_threshold": 0.6
    },
    {
        "id": "RAG-Q50",
        "domain": "System Design",
        "query": "How does database sharding partition data across horizontal clusters using consistent hashing?",
        "expected_keywords": ["sharding", "partition", "horizontal", "consistent hashing", "cluster", "shard key"],
        "min_relevance_threshold": 0.6
    }
]
