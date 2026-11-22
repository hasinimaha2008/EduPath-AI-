"""
Academic-to-Industry Taxonomy & Seed Dataset for EduPath AI.
Comprehensive Multi-Subject Curricula (16 Subjects), Module/Unit Structures,
Subtopics, Emerging Industry Technologies, and Official Educational References.
"""

CAREER_ROLES = [
    {
        "title": "Python Developer",
        "slug": "python-developer",
        "description": "Designs and develops backend services, data automation scripts, REST APIs, and core business logic using Python.",
        "salary_range": "$85,000 - $130,000",
        "industry_demand": "Very High",
        "icon_name": "Code"
    },
    {
        "title": "Data Analyst",
        "slug": "data-analyst",
        "description": "Inspects, cleans, transforms, and models data to uncover actionable insights, automate reporting, and empower business decisions.",
        "salary_range": "$75,000 - $115,000",
        "industry_demand": "High",
        "icon_name": "BarChart3"
    },
    {
        "title": "Data Scientist",
        "slug": "data-scientist",
        "description": "Leverages statistical methods, machine learning algorithms, and exploratory data analysis to build predictive products.",
        "salary_range": "$105,000 - $160,000",
        "industry_demand": "High",
        "icon_name": "TrendingUp"
    },
    {
        "title": "Web Developer",
        "slug": "web-developer",
        "description": "Builds interactive, performant, and accessible user interfaces and web applications using modern web standards and frameworks.",
        "salary_range": "$80,000 - $125,000",
        "industry_demand": "Very High",
        "icon_name": "Globe"
    },
    {
        "title": "Backend Developer",
        "slug": "backend-developer",
        "description": "Architects server-side logic, secure REST/GraphQL APIs, database architectures, microservices, and system scalability.",
        "salary_range": "$95,000 - $145,000",
        "industry_demand": "Very High",
        "icon_name": "Server"
    },
    {
        "title": "Database Developer",
        "slug": "database-developer",
        "description": "Designs robust relational schemas, tunes complex SQL queries, implements indexes, and manages ACID data pipelines.",
        "salary_range": "$90,000 - $135,000",
        "industry_demand": "High",
        "icon_name": "Database"
    },
    {
        "title": "Machine Learning Engineer",
        "slug": "machine-learning-engineer",
        "description": "Develops, trains, evaluates, and deploys scalable machine learning models into production inference pipelines.",
        "salary_range": "$115,000 - $175,000",
        "industry_demand": "Very High",
        "icon_name": "Cpu"
    },
    {
        "title": "Cybersecurity Analyst",
        "slug": "cybersecurity-analyst",
        "description": "Protects organizational infrastructure, assesses vulnerabilities, monitors network traffic, and implements access control policies.",
        "salary_range": "$90,000 - $140,000",
        "industry_demand": "Extremely High",
        "icon_name": "ShieldAlert"
    },
    {
        "title": "Cloud Solutions Architect",
        "slug": "cloud-solutions-architect",
        "description": "Architects highly resilient multi-cloud infrastructures, Kubernetes container orchestration, serverless microservices, and automated GitOps CI/CD pipelines.",
        "salary_range": "$120,000 - $185,000",
        "industry_demand": "Extremely High",
        "icon_name": "Cloud"
    },
    {
        "title": "AI Engineer",
        "slug": "ai-engineer",
        "description": "Architects enterprise Generative AI systems, RAG retrieval pipelines, LLM fine-tuning, vector database indexing, and autonomous multi-agent workflows.",
        "salary_range": "$125,000 - $190,000",
        "industry_demand": "Extremely High",
        "icon_name": "Brain"
    }
]

SUBJECTS_AND_TOPICS = [
    # 1. DBMS
    {
        "name": "DBMS",
        "code": "CS-301",
        "category": "Data Systems",
        "icon_name": "Database",
        "description": "Relational data modeling, SQL standards, normalization, storage engines, indexing, transactions, and modern vector databases.",
        "topics": [
            {
                "name": "SQL & Relational Queries",
                "description": "SELECT queries, complex aggregations, window functions, CTEs, and relational algebra.",
                "module_name": "Module 1: Relational Foundations",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "ISO/IEC 9075:2023 (SQL Standard) / Silberschatz Database Concepts",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Relational Algebra Operators", "Complex Joins & Subqueries", "Window Functions (OVER, PARTITION BY)", "Common Table Expressions (WITH)"]
            },
            {
                "name": "Database Normalization & Functional Dependencies",
                "description": "Functional dependencies, closure sets, canonical cover, 1NF through BCNF and 4NF.",
                "module_name": "Module 2: Schema Design & Integrity",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "ACM Computing Surveys / Elmasri & Navathe Fundamentals of Database Systems",
                "last_updated_date": "2025-Q2",
                "subtopics": ["Functional Dependency Inference", "1NF, 2NF, 3NF Decomposition", "Boyce-Codd Normal Form (BCNF)", "Lossless Join & Dependency Preservation"]
            },
            {
                "name": "Indexing & Query Optimization",
                "description": "B+ Trees, Hash indexes, GiST/GIN indexes, cost-based query optimization, execution plans.",
                "module_name": "Module 3: Storage & Query Engine",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "PostgreSQL Internals / IEEE Transactions on Knowledge and Data Engineering",
                "last_updated_date": "2025-Q4",
                "subtopics": ["B+ Tree Structure & Balancing", "Clustered vs Secondary Indexes", "Query Execution Plans & EXPLAIN ANALYZE", "Bitmap Index Scans & Index Selectivity"]
            },
            {
                "name": "Transactions & ACID Properties",
                "description": "Concurrency control, Serializability, Strict 2PL, MVCC, and write-ahead logging (WAL).",
                "module_name": "Module 4: Concurrency & Fault Recovery",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Transaction Processing: Concepts & Techniques (Jim Gray) / VLDB Endowments",
                "last_updated_date": "2025-Q3",
                "subtopics": ["ACID Guarantees & Anomalies", "Two-Phase Locking (2PL) & Deadlocks", "Multi-Version Concurrency Control (MVCC)", "ARIES Recovery & Write-Ahead Logging (WAL)"]
            },
            {
                "name": "Vector Databases & Semantic Embeddings",
                "description": "High-dimensional vector storage, HNSW graphs, IVFFlat indexing, and pgvector for AI applications.",
                "module_name": "Module 5: Emerging Modern Data Systems",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "ACM SIGMOD 2024 / pgvector Official Documentation & RFCs",
                "last_updated_date": "2026-Q1",
                "subtopics": ["High-Dimensional Vector Embeddings", "HNSW (Hierarchical Navigable Small World)", "Cosine Similarity vs Dot Product Distance", "Hybrid Search (Full-Text + Vector Reranking)"]
            }
        ]
    },

    # 2. Data Structures and Algorithms
    {
        "name": "Data Structures and Algorithms",
        "code": "CS-201",
        "category": "Core Computer Science",
        "icon_name": "Binary",
        "description": "Fundamental and advanced data structures, asymptotic Big-O analysis, sorting, graph traversal, and dynamic programming.",
        "topics": [
            {
                "name": "Asymptotic Analysis & Big-O",
                "description": "Mathematical complexity bounds, Master theorem, recursion trees, and amortized time/space analysis.",
                "module_name": "Module 1: Foundations of Complexity",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Cormen, Leiserson, Rivest, Stein (CLRS) Introduction to Algorithms 4th Ed.",
                "last_updated_date": "2025-Q2",
                "subtopics": ["Big-O, Omega, and Theta Bounds", "Master Theorem for Recurrences", "Amortized Analysis (Accounting & Potential Methods)", "Space Complexity & Auxiliary Memory"]
            },
            {
                "name": "Arrays, Hashing & String Algorithms",
                "description": "Dynamic arrays, open addressing vs chaining in hash tables, Rabin-Karp, and KMP pattern matching.",
                "module_name": "Module 2: Linear Structures & Hashing",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "ACM SODA / Knuth The Art of Computer Programming",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Hash Collision Resolution (Robin Hood & Cuckoo)", "Prefix Sums & Two Pointers", "Knuth-Morris-Pratt (KMP) Algorithm", "Rolling Hash & Rabin-Karp"]
            },
            {
                "name": "Trees, Heaps & Self-Balancing Structures",
                "description": "AVL trees, Red-Black trees, binary heaps, priority queues, and segment trees.",
                "module_name": "Module 3: Hierarchical Structures",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "CLRS 4th Ed. / IEEE Computer Society Curriculum 2023",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Tree Rotations in AVL & Red-Black Trees", "Binary Min/Max Heaps & Heapify", "Trie Data Structure & Autocomplete", "Segment Trees & Range Minimum Queries"]
            },
            {
                "name": "Graph Algorithms & Shortest Paths",
                "description": "BFS, DFS, Dijkstra, Bellman-Ford, Floyd-Warshall, Kruskal, Prim, and topological sorting.",
                "module_name": "Module 4: Graph Theory & Networks",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Tarjan Graph Algorithms / Kleinberg & Tardos Algorithm Design",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Breadth-First & Depth-First Search", "Dijkstra's Algorithm with Min-Heap", "Bellman-Ford & Negative Cycles Detection", "Topological Sort & Cycle Detection in DAGs"]
            },
            {
                "name": "Dynamic Programming & Greedy Strategies",
                "description": "Optimal substructure, overlapping subproblems, memoization, tabulation, interval scheduling.",
                "module_name": "Module 5: Advanced Optimization Techniques",
                "order_index": 5,
                "is_emerging": False,
                "source_reference": "CLRS 4th Ed. / Sedgewick Algorithms",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Memoization vs Tabulation Approaches", "0/1 Knapsack & Unbounded Variations", "Longest Common Subsequence & Edit Distance", "Greedy Choice Property & Proofs"]
            },
            {
                "name": "Cache-Oblivious Data Structures & Approximate Nearest Neighbor",
                "description": "Memory hierarchy optimization, van Emde Boas layout, locality-sensitive hashing for high-dimensional search.",
                "module_name": "Module 6: Modern Algorithmic Innovations",
                "order_index": 6,
                "is_emerging": True,
                "source_reference": "ACM Trans. on Algorithms / Stanford CS246 Mining Massive Datasets",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Cache Oblivious B-Trees & Memory Locality", "Locality Sensitive Hashing (LSH)", "Skip Graphs & Distributed Indexing", "Succinct & Compact Bit-Vector Representations"]
            }
        ]
    },

    # 3. Python Programming
    {
        "name": "Python Programming",
        "code": "CS-101-PY",
        "category": "Programming Languages",
        "icon_name": "Code2",
        "description": "Modern Python 3.12+, OOP, generators, decorators, memory management, AsyncIO concurrency, and AI ecosystem libraries.",
        "topics": [
            {
                "name": "Python Core Syntax & Data Model",
                "description": "Dynamic typing, mutable vs immutable types, comprehensions, iterators, and generators.",
                "module_name": "Module 1: Language Fundamentals & Data Model",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Official Python 3.12 Documentation / Fluent Python (Luciano Ramalho)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Underlying Data Model & Dunder Methods", "List, Dict & Set Comprehensions", "Generators & Memory-Efficient Yielding", "Scopes (LEGB Rule) & Closures"]
            },
            {
                "name": "Object-Oriented Programming & Metaprogramming",
                "description": "Inheritance, composition, abstract base classes, decorators, descriptors, and metaclasses.",
                "module_name": "Module 2: Advanced OOP & Metaprogramming",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Python Software Foundation PEP 3119 / PEP 487",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Abstract Base Classes (abc module)", "Decorators with Arguments & Wraps", "Attribute Descriptors & __get__/__set__", "Metaclasses & Class Construction Hooks"]
            },
            {
                "name": "Concurrency with AsyncIO & Multiprocessing",
                "description": "Async/await syntax, event loop mechanics, TaskGroup, multiprocessing vs threading, and GIL internals.",
                "module_name": "Module 3: High-Performance Concurrency",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "PEP 492 / PEP 654 (Exception Groups) / Python AsyncIO Docs",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Event Loop Architecture & Coroutines", "TaskGroups & Structured Concurrency", "Global Interpreter Lock (GIL) Behavior", "Multiprocessing & Shared Memory Pools"]
            },
            {
                "name": "Type Annotations, Pydantic & Production Tooling",
                "description": "Static type checking with Mypy, Generic types, Pydantic V2 validation, and modern Ruff/UV tooling.",
                "module_name": "Module 4: Enterprise Tooling & Strict Typing",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "PEP 484 / PEP 585 / Pydantic V2 Architecture Guide",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Type Hints, Generics & TypeVar", "Pydantic V2 BaseModel Validation", "Modern Packaging with UV & Poetry", "Automated Testing with Pytest & Mocks"]
            },
            {
                "name": "Free-Threaded Python & AI Agent Orchestration",
                "description": "PEP 703 (No-GIL Python 3.13), JIT compilation, LiteLLM, and autonomous LangGraph/CrewAI agent pipelines.",
                "module_name": "Module 5: Emerging Python & AI Infrastructure",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "Python PEP 703 (Free-Threaded CPython) / LangGraph Documentation 2025",
                "last_updated_date": "2026-Q1",
                "subtopics": ["CPython No-GIL (Free-Threading Mode)", "Tier-2 JIT Compiler Architecture in Python 3.13+", "Async AI Agent Tool Calling Pipelines", "Structured Outputs with Instructor & Pydantic"]
            }
        ]
    },

    # 4. Java Programming
    {
        "name": "Java Programming",
        "code": "CS-102-JV",
        "category": "Programming Languages",
        "icon_name": "Coffee",
        "description": "Modern Java SE 21 LTS, JVM memory architecture, Collections, Streams, Virtual Threads (Project Loom), and Spring Boot 3.",
        "topics": [
            {
                "name": "Java Syntax, JVM Architecture & OOP",
                "description": "Compilation lifecycle, bytecode, ClassLoader, Heap vs Stack, GC algorithms, encapsulation, polymorphism.",
                "module_name": "Module 1: JVM Architecture & Core OOP",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Oracle Java SE 21 Specification / Effective Java (Joshua Bloch)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["JVM Memory Layout (Heap, Stack, Metaspace)", "Garbage Collection (G1, ZGC) Mechanics", "Interface Contracts & Default Methods", "Polymorphism & Dynamic Method Dispatch"]
            },
            {
                "name": "Java Collections Framework & Generics",
                "description": "HashMap internals, collision trees, ConcurrentHashMap, generic type erasure, wildcards.",
                "module_name": "Module 2: Collections & Generic Types",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Oracle Java Platform API Specification / ACM Queue",
                "last_updated_date": "2025-Q3",
                "subtopics": ["HashMap Bucket Structure & Treeify Threshold", "ConcurrentHashMap Thread-Safety Mechanism", "Generics Type Erasure & Bridge Methods", "Covariance & Contravariance (PECS Rule)"]
            },
            {
                "name": "Modern Java Features: Streams, Records & Pattern Matching",
                "description": "Functional interfaces, lazy stream pipelines, Records, sealed classes, pattern matching for switch.",
                "module_name": "Module 3: Modern Functional Java (Java 17-21)",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "OpenJDK Projects / JEP 440 & JEP 441",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Stream API & Lazy Evaluation Pipelines", "Records for Immutable Data Modeling", "Sealed Classes & Interfaces", "Pattern Matching for switch Expressions"]
            },
            {
                "name": "Concurrency, Virtual Threads & Project Loom",
                "description": "Platform threads vs Virtual threads, structured concurrency, ForkJoinPool, and atomic variables.",
                "module_name": "Module 4: High-Throughput Concurrency",
                "order_index": 4,
                "is_emerging": True,
                "source_reference": "JEP 444 (Virtual Threads) / Brian Goetz Concurrency Guides",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Carrier Threads vs Continuation Stacks", "Structured Concurrency API (JEP 453)", "Scoped Values (JEP 446)", "Non-blocking ReentrantLock & Semaphores"]
            },
            {
                "name": "Spring Boot 3 & GraalVM Native Image Compilation",
                "description": "Spring Framework 6, dependency injection, reactive WebFlux, ahead-of-time (AOT) GraalVM native binaries.",
                "module_name": "Module 5: Emerging Enterprise Microservices",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "Spring Framework 6.2 Docs / GraalVM Enterprise Guide",
                "last_updated_date": "2026-Q1",
                "subtopics": ["IoC Container & Component Scanning", "Reactive Microservices with WebFlux", "GraalVM AOT Native Image Compilation", "Observability with Micrometer & OpenTelemetry"]
            }
        ]
    },

    # 5. C Programming
    {
        "name": "C Programming",
        "code": "CS-103-C",
        "category": "Programming Languages",
        "icon_name": "Terminal",
        "description": "Foundational systems programming, memory addressing, pointers, dynamic memory allocation, POSIX I/O, and C23 standards.",
        "topics": [
            {
                "name": "Data Types, Bitwise Logic & Memory Representation",
                "description": "Integer representation, two's complement, IEEE 754 floating point, bit masking, and bit shifting.",
                "module_name": "Module 1: Bitwise Logic & Machine Representation",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Kernighan & Ritchie (K&R) The C Programming Language / ISO/IEC 9899",
                "last_updated_date": "2025-Q2",
                "subtopics": ["Two's Complement & Integer Overflow", "Bitwise Operators (&, |, ^, ~, <<, >>)", "Bit Fields in System Registers", "Type Conversions & Integer Promotions"]
            },
            {
                "name": "Pointers, Pointer Arithmetic & Address Space",
                "description": "Memory addresses, pointer arithmetic, void pointers, function pointers, and array decays.",
                "module_name": "Module 2: Pointers & Address Space",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "K&R C / Computer Systems: A Programmer's Perspective (CS:APP)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Pointer Dereferencing & Indirection", "Pointer Arithmetic & Array Offsets", "Double Pointers & Dynamic 2D Arrays", "Function Pointers & Callback Architectures"]
            },
            {
                "name": "Dynamic Memory Management & Memory Safety",
                "description": "Heap allocation (malloc, calloc, realloc, free), memory fragmentation, memory leaks, dangling pointers.",
                "module_name": "Module 3: Heap Management & Memory Safety",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "CERT C Secure Coding Standard / Valgrind Documentation",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Heap Boundary Tags & Chunks", "Memory Leak Detection with Valgrind / ASan", "Dangling Pointers & Double Free Prevention", "Custom Memory Arena Allocators"]
            },
            {
                "name": "Structs, Memory Alignment & Binary File I/O",
                "description": "Struct padding, byte alignment, unions for type punning, unbuffered POSIX file descriptors, and binary I/O.",
                "module_name": "Module 4: Data Structures & System File I/O",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Advanced Programming in the UNIX Environment (APUE) Stevens",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Struct Packing & Alignment Rules", "Unions & Type Punning Applications", "POSIX open, read, write, lseek Calls", "Buffered vs Unbuffered Standard I/O"]
            },
            {
                "name": "C23 Standard Features & WebAssembly Compilation",
                "description": "Modern C23 keywords (constexpr, typeof, nullptr), Clang AddressSanitizer, and compiling C to WebAssembly.",
                "module_name": "Module 5: Emerging Modern C & WebAssembly",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "ISO/IEC 9899:2024 (C23 Standard) / W3C WebAssembly Specification",
                "last_updated_date": "2026-Q1",
                "subtopics": ["C23 nullptr, constexpr, and typeof Keywords", "AddressSanitizer (ASan) & UndefinedBehaviorSanitizer", "Emscripten Compiler Pipeline for WebAssembly", "Zero-Copy Data Pipelines in Modern C"]
            }
        ]
    },

    # 6. Operating Systems
    {
        "name": "Operating Systems",
        "code": "CS-302",
        "category": "Systems & Infrastructure",
        "icon_name": "Server",
        "description": "Kernel architecture, process scheduling, synchronization primitives, virtual memory paging, file systems, and eBPF.",
        "topics": [
            {
                "name": "Process Management & CPU Scheduling",
                "description": "Process Control Block (PCB), context switching, CPU scheduling algorithms (CFS, Multi-level feedback queues).",
                "module_name": "Module 1: Process Lifecycle & Scheduling",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Silberschatz, Galvin, Gagne Operating System Concepts 10th Ed.",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Process Control Block (PCB) & State Transitions", "Hardware Context Switch Mechanics", "Linux Completely Fair Scheduler (CFS)", "Multi-Level Feedback Queue (MLFQ) Scheduling"]
            },
            {
                "name": "Concurrency, Mutexes & Deadlocks",
                "description": "Race conditions, semaphores, mutexes, condition variables, deadlock detection, and Banker's algorithm.",
                "module_name": "Module 2: Synchronization & Concurrency Control",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Dijkstra Cooperating Sequential Processes / Tanenbaum Modern Operating Systems",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Critical Section Problem & Peterson's Algorithm", "Counting & Binary Semaphores", "Deadlock 4 Coffman Conditions", "Banker's Resource Allocation Safety Algorithm"]
            },
            {
                "name": "Virtual Memory, Paging & TLB Mechanics",
                "description": "Page tables, Translation Lookaside Buffer (TLB), page faults, demand paging, and LRU replacement algorithms.",
                "module_name": "Module 3: Memory Virtualization",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "CS:APP 3rd Ed. / OSTEP (Remzi Arpaci-Dusseau)",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Multi-Level Page Table Translation", "TLB Miss Handling & Performance Penalty", "Page Replacement (LRU, Clock, Optimal)", "Thrashing & Working Set Model"]
            },
            {
                "name": "Storage Architecture & File Systems",
                "description": "Inodes, directory structures, journaling, disk scheduling, and asynchronous I/O (io_uring).",
                "module_name": "Module 4: Storage Engines & File Systems",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Linux Kernel Architecture / Tanenbaum Modern OS",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Inode Table & Direct/Indirect Data Pointers", "Ext4 Journaling & Consistency Recovery", "Linux io_uring High-Performance Asynchronous I/O", "Virtual File System (VFS) Abstraction Layer"]
            },
            {
                "name": "eBPF & Modern Linux Containerization Internals",
                "description": "Linux namespaces, cgroups v2, eBPF in-kernel programmable verification, and microVMs.",
                "module_name": "Module 5: Emerging Systems & Observability",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "Linux Foundation eBPF / Brendan Gregg Systems Performance 2nd Ed.",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Linux Namespaces (PID, Mount, Net, IPC)", "Control Groups (cgroups v2) Resource Limits", "eBPF In-Kernel Bytecode & JIT Safety", "MicroVMs (Firecracker / Cloud-Hypervisor)"]
            }
        ]
    },

    # 7. Computer Networks
    {
        "name": "Computer Networks",
        "code": "CS-303",
        "category": "Systems & Infrastructure",
        "icon_name": "Network",
        "description": "TCP/IP protocol stack, routing algorithms (OSPF, BGP), transport reliability, HTTP/3 QUIC, and Zero Trust security.",
        "topics": [
            {
                "name": "Network Protocol Stacks & Physical/Data Link Layers",
                "description": "OSI 7-layer model, TCP/IP 4-layer model, Ethernet frames, MAC addresses, ARP protocol, VLANs.",
                "module_name": "Module 1: Protocol Architectures & Link Layer",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Kurose & Ross Computer Networking: A Top-Down Approach 8th Ed.",
                "last_updated_date": "2025-Q3",
                "subtopics": ["OSI vs TCP/IP Encapsulation", "Address Resolution Protocol (ARP) Mechanics", "Ethernet Frame Structure & CSMA/CD", "VLAN Tagging (802.1Q) & Virtual Switches"]
            },
            {
                "name": "IPv4/IPv6 Subnetting & Network Layer Routing",
                "description": "CIDR notation, NAT traversal, distance vector vs link state routing, OSPF, and BGP inter-domain routing.",
                "module_name": "Module 2: Network Layer & Global Routing",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "IETF RFC 791 (IPv4) / RFC 8200 (IPv6) / Peterson & Davie Computer Networks",
                "last_updated_date": "2025-Q3",
                "subtopics": ["CIDR Subnet Calculations & VLSM", "Network Address Translation (NAT) & PAT", "OSPF Dijkstra Link-State Protocol", "Border Gateway Protocol (BGP) Autonomous Systems"]
            },
            {
                "name": "TCP Reliability, Flow Control & Congestion Control",
                "description": "TCP 3-way handshake, 4-way termination, sliding window flow control, and TCP BBR/Cubic congestion algorithms.",
                "module_name": "Module 3: Transport Layer Reliability",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "IETF RFC 9293 (TCP Specification) / ACM SIGCOMM",
                "last_updated_date": "2025-Q4",
                "subtopics": ["TCP 3-Way Handshake & SYN Floods", "Sliding Window Flow Control & Buffer Sizing", "TCP Congestion Control (Slow Start, Fast Retransmit)", "Modern TCP BBR (Bottleneck Bandwidth and RTT)"]
            },
            {
                "name": "Application Protocols: HTTP/2, DNS & TLS 1.3",
                "description": "DNS resolution hierarchy, HTTP/2 multiplexing, TLS 1.3 handshake mechanics, and certificate authorities.",
                "module_name": "Module 4: Application Layer & Transport Security",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "IETF RFC 8446 (TLS 1.3) / RFC 7540 (HTTP/2)",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Recursive vs Iterative DNS Resolution", "HTTP/2 Binary Framing & Stream Multiplexing", "TLS 1.3 1-RTT Handshake & Key Exchange", "Public Key Certificates & OCSP Stapling"]
            },
            {
                "name": "HTTP/3 QUIC & Zero Trust Network Architecture",
                "description": "UDP-based QUIC transport protocol, 0-RTT connection resumption, Software-Defined Perimeter (SDP), and ZTNA.",
                "module_name": "Module 5: Emerging Networking Paradigms",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "IETF RFC 9000 (QUIC) / NIST SP 800-207 Zero Trust Architecture",
                "last_updated_date": "2026-Q1",
                "subtopics": ["QUIC Connection Migration & 0-RTT Resumption", "Eliminating Head-of-Line Blocking over UDP", "Zero Trust Network Access (ZTNA) Microsegmentation", "Service Mesh Architecture with Envoy Proxy"]
            }
        ]
    },

    # 8. Software Engineering
    {
        "name": "Software Engineering",
        "code": "CS-304",
        "category": "Software & Security",
        "icon_name": "Layers",
        "description": "SDLC methodologies, Agile/Scrum, UML design, SOLID principles, GoF design patterns, CI/CD, and AI-assisted workflows.",
        "topics": [
            {
                "name": "Software Lifecycles & Agile Methodologies",
                "description": "Waterfall, Spiral, V-Model, Agile Manifesto, Scrum sprints, user stories, and Kanban WIP limits.",
                "module_name": "Module 1: Development Methodologies & Agile",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "IEEE Software Engineering Body of Knowledge (SWEBOK v4) / Agile Alliance",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Iterative vs Predictive Lifecycle Models", "Scrum Ceremonies (Planning, Standup, Retro)", "User Story Estimation & Story Points", "Kanban Flow Optimization & WIP Limits"]
            },
            {
                "name": "Architectural Patterns & Microservices",
                "description": "Monolith vs Microservices, Event-Driven Architecture, CQRS, Domain-Driven Design (DDD).",
                "module_name": "Module 2: System Architecture & Decomposition",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Martin Fowler Software Architecture / Eric Evans Domain-Driven Design",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Domain-Driven Design (Bounded Contexts & Aggregates)", "Event-Driven Architecture with Message Brokers", "CQRS & Event Sourcing Patterns", "Microservice Decomposition & Saga Pattern"]
            },
            {
                "name": "SOLID Principles & Gang of Four Design Patterns",
                "description": "Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion, Creational, Structural, Behavioral patterns.",
                "module_name": "Module 3: Object-Oriented Design & Patterns",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "Design Patterns: Elements of Reusable Object-Oriented Software (GoF) / Clean Architecture (Robert Martin)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["SOLID Architectural Principles with Real Examples", "Factory, Singleton & Builder Patterns", "Adapter, Decorator & Proxy Patterns", "Strategy, Observer & Command Patterns"]
            },
            {
                "name": "Automated Testing, CI/CD Pipelines & DevOps",
                "description": "Unit testing, integration testing, TDD, end-to-end testing, GitHub Actions, and automated deployment pipelines.",
                "module_name": "Module 4: Quality Engineering & DevOps",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "DORA State of DevOps Research / Continuous Delivery (Humble & Farley)",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Test-Driven Development (TDD) Red-Green-Refactor", "Test Pyramids & Mocking Isolation", "CI/CD Pipeline Automation (GitHub Actions / GitLab)", "Blue-Green & Canary Deployment Strategies"]
            },
            {
                "name": "AI-Assisted Software Engineering & Distributed Tracing",
                "description": "LLM code agents, automated PR reviews, OpenTelemetry distributed tracing, and Chaos Engineering.",
                "module_name": "Module 5: Emerging SE Paradigms",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "ACM Trans. on Software Engineering / OpenTelemetry W3C Trace Context",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Autonomous AI Coding Agents in CI/CD", "OpenTelemetry Distributed Spans & Traces", "Chaos Engineering & Fault Injection (Gremlin/Chaos Mesh)", "Site Reliability Engineering (SLO/SLI/Error Budgets)"]
            }
        ]
    },

    # 9. Artificial Intelligence
    {
        "name": "Artificial Intelligence",
        "code": "CS-401",
        "category": "AI & Data Science",
        "icon_name": "Brain",
        "description": "Intelligent agents, heuristic search (A*), adversarial games, propositional/predicate logic, and autonomous agent systems.",
        "topics": [
            {
                "name": "Intelligent Agents & Problem-Solving Search",
                "description": "Rational agent architectures, state spaces, uninformed search (BFS, DFS), and informed heuristic search (A*, IDA*).",
                "module_name": "Module 1: Agent Architectures & Heuristic Search",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Russell & Norvig Artificial Intelligence: A Modern Approach (AIMA 4th Ed.)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["PEAS (Performance, Environment, Actuators, Sensors)", "A* Algorithm & Admissible Heuristics", "Heuristic Consistency & Monotonicity", "Iterative Deepening A* (IDA*) Search"]
            },
            {
                "name": "Adversarial Search & Game Playing",
                "description": "Minimax algorithm, Alpha-Beta pruning, evaluation functions, Monte Carlo Tree Search (MCTS).",
                "module_name": "Module 2: Adversarial Games & Decision Trees",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "AIMA 4th Ed. / Nature AlphaGo & MCTS Publications",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Minimax Strategy in Zero-Sum Games", "Alpha-Beta Pruning Efficiency & Cutoffs", "Evaluation Functions for Intermediate States", "Monte Carlo Tree Search (MCTS) Selection & Rollout"]
            },
            {
                "name": "Knowledge Representation, Logic & Inference",
                "description": "Propositional logic, First-Order Logic (FOL), resolution theorem proving, forward/backward chaining, and ontologies.",
                "module_name": "Module 3: Knowledge Representation & Logic Engines",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "AIMA 4th Ed. / Handbook of Knowledge Representation",
                "last_updated_date": "2025-Q4",
                "subtopics": ["First-Order Logic Quantifiers (Universal & Existential)", "Conjunctive Normal Form (CNF) Conversion", "Resolution Refutation Proving", "Forward & Backward Chaining Inference"]
            },
            {
                "name": "Probabilistic Reasoning & Bayesian Networks",
                "description": "Bayes' theorem, conditional independence, Bayesian Belief Networks, variable elimination, Markov networks.",
                "module_name": "Module 4: Uncertainty & Probabilistic Reasoning",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Judea Pearl Probabilistic Reasoning in Intelligent Systems / AIMA 4th Ed.",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Conditional Probability & Bayes' Rule", "Bayesian Network Direct Acyclic Graphs", "D-Separation & Conditional Independence", "Exact Inference via Variable Elimination"]
            },
            {
                "name": "Autonomous Multi-Agent Systems & Tool-Calling Agents",
                "description": "ReAct prompting, autonomous goal-directed agents, tool retrieval, multi-agent negotiation, and safety alignment.",
                "module_name": "Module 5: Emerging Autonomous AI Systems",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "AAAI / NeurIPS 2024-2025 Multi-Agent Planning Papers",
                "last_updated_date": "2026-Q1",
                "subtopics": ["ReAct (Reason + Act) Loop Architectures", "Tool Definition, Calling & Schema Verification", "Multi-Agent Collaboration & Consensus Protocols", "AI Alignment, Hallucination Mitigation & Guardrails"]
            }
        ]
    },

    # 10. Machine Learning
    {
        "name": "Machine Learning",
        "code": "CS-402",
        "category": "AI & Data Science",
        "icon_name": "TrendingUp",
        "description": "Statistical learning theory, supervised regression/classification, ensemble methods (XGBoost), clustering, and MLOps.",
        "topics": [
            {
                "name": "Statistical Learning & Preprocessing Pipelines",
                "description": "Bias-variance tradeoff, regularized cost functions (Ridge, Lasso), feature scaling, and categorical encoding.",
                "module_name": "Module 1: Foundations of Statistical Learning",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Hastie, Tibshirani, Friedman The Elements of Statistical Learning 2nd Ed.",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Bias-Variance Decomposition & Overfitting", "L1 Lasso vs L2 Ridge Regularization", "Robust Scaling & Target Encoding", "K-Fold Stratified Cross-Validation"]
            },
            {
                "name": "Linear Models, Logistic Regression & Support Vector Machines",
                "description": "Gradient descent optimization, maximum margin hyperplanes, SVM kernels (RBF, Polynomial), loss functions.",
                "module_name": "Module 2: Supervised Classifiers & Optimizers",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Bishop Pattern Recognition and Machine Learning / Scikit-Learn Docs",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Batch, Stochastic & Mini-Batch Gradient Descent", "Log-Loss (Binary Cross-Entropy) Mathematical Formulation", "Maximum Margin Hyperplane & Slack Variables", "Kernel Trick & Radial Basis Function (RBF) Kernel"]
            },
            {
                "name": "Decision Trees & Gradient Boosted Ensembles",
                "description": "Entropy, Gini impurity, Random Forests, AdaBoost, Gradient Boosting, XGBoost, and LightGBM.",
                "module_name": "Module 3: Tree Ensembles & Boosting",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "ACM SIGKDD / XGBoost: A Scalable Tree Boosting System (Chen & Guestrin)",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Information Gain & Gini Impurity Splitting", "Bagging & Out-of-Bag (OOB) Error in Random Forests", "Gradient Boosted Decision Trees (GBDT) Loss Minimization", "XGBoost Regularization & Histogram Pruning"]
            },
            {
                "name": "Unsupervised Clustering & Dimensionality Reduction",
                "description": "K-Means, DBSCAN density clustering, Principal Component Analysis (PCA), and t-SNE embedding.",
                "module_name": "Module 4: Unsupervised Learning & Embeddings",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Elements of Statistical Learning / JMLR",
                "last_updated_date": "2025-Q4",
                "subtopics": ["K-Means++ Initialization & Silhouette Coefficient", "DBSCAN Core Points, Epsilon & MinPts", "Principal Component Analysis (PCA) Eigenvectors", "t-SNE & UMAP Manifold Learning for High-Dim Data"]
            },
            {
                "name": "MLOps, Model Monitoring & RAG Feature Stores",
                "description": "Model drift detection, continuous training pipelines, MLflow tracking, Feast feature stores, and RAG architectures.",
                "module_name": "Module 5: Emerging MLOps & Production AI",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "Google MLOps Architecture Guide / MLflow 2.15 Documentation",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Data Drift & Concept Drift Statistical Tests (KS-Test)", "Automated Pipeline Orchestration with Prefect / Airflow", "Model Registries, Artifact Versioning & Staging", "Retrieval-Augmented Generation (RAG) Architecture"]
            }
        ]
    },

    # 11. Deep Learning
    {
        "name": "Deep Learning",
        "code": "CS-403",
        "category": "AI & Data Science",
        "icon_name": "Cpu",
        "description": "Deep neural networks, backpropagation, CNNs, RNNs/LSTMs, Transformer attention models, and parameter-efficient fine-tuning.",
        "topics": [
            {
                "name": "Neural Network Fundamentals & Backpropagation",
                "description": "Perceptrons, multi-layer feedforward networks, activation functions (ReLU, GELU), computational graphs, AdamW optimizer.",
                "module_name": "Module 1: Foundations of Deep Networks",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Goodfellow, Bengio, Courville Deep Learning (MIT Press)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Computational Graphs & Automatic Differentiation", "Activation Function Landscapes (ReLU, GELU, Swish)", "Vanishing & Exploding Gradients (Batch Normalization)", "AdamW Optimization & Cosine Annealing Schedules"]
            },
            {
                "name": "Convolutional Neural Networks (CNNs) & Vision",
                "description": "Convolution operations, pooling, receptive fields, ResNet skip connections, vision backbones.",
                "module_name": "Module 2: Computer Vision & Convolutions",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "IEEE CVPR / Deep Residual Learning for Image Recognition (He et al.)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Kernel Convolutions, Stride & Padding Mathematics", "Receptive Field Expansion & Dilated Convolutions", "Residual Skip Connections in ResNet", "Transfer Learning & Fine-Tuning Vision Backbones"]
            },
            {
                "name": "Sequence Models, LSTMs & Recurrent Architectures",
                "description": "Recurrent neural networks, vanishing gradients in time, Long Short-Term Memory (LSTM) gates, GRUs.",
                "module_name": "Module 3: Recurrent & Sequential Modeling",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "Hochreiter & Schmidhuber LSTM (Neural Computation) / Goodfellow Deep Learning",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Backpropagation Through Time (BPTT)", "LSTM Forget, Input, and Output Gates", "Gated Recurrent Units (GRU) Simplification", "Bidirectional Sequence Processing"]
            },
            {
                "name": "Transformer Architecture & Self-Attention Mechanics",
                "description": "Scaled dot-product attention, multi-head attention, positional encodings, encoder-decoder models, BERT and GPT.",
                "module_name": "Module 4: Attention Mechanisms & Transformers",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "NeurIPS 2017: Attention Is All You Need (Vaswani et al.)",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Query, Key, Value Matrix Operations", "Multi-Head Self-Attention Calculation", "Rotary Positional Embeddings (RoPE)", "Causal Masking in Auto-Regressive Decoders"]
            },
            {
                "name": "Parameter-Efficient Fine-Tuning (LoRA / QLoRA) & Quantization",
                "description": "Low-Rank Adaptation (LoRA), 4-bit NormalFloat quantization, FlashAttention-2, and instruction tuning.",
                "module_name": "Module 5: Emerging Generative Deep Learning",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "ICLR 2022: LoRA (Hu et al.) / NeurIPS 2023: QLoRA (Dettmers et al.)",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Low-Rank Adaptation (LoRA) Weight Decomposition", "4-Bit NormalFloat Quantization & Double Quantization", "FlashAttention IO-Aware Memory Optimization", "Direct Preference Optimization (DPO) Alignment"]
            }
        ]
    },

    # 12. Data Science
    {
        "name": "Data Science",
        "code": "CS-404",
        "category": "AI & Data Science",
        "icon_name": "BarChart3",
        "description": "Pandas, NumPy, statistical distributions, hypothesis testing (ANOVA, T-Tests), data storytelling, and high-performance DuckDB.",
        "topics": [
            {
                "name": "Numerical Computing & Array Broadcasting with NumPy",
                "description": "Multidimensional arrays, vectorized operations, broadcasting semantics, linear algebra matrix decompositions.",
                "module_name": "Module 1: Vectorized Numerical Computing",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Nature: Array Programming with NumPy (Harris et al.) / NumPy Docs",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Memory Strides & C vs Fortran Contiguity", "Array Broadcasting Rules & Dimension Alignment", "Vectorized Aggregations & Boolean Masking", "Singular Value Decomposition (SVD) with NumPy"]
            },
            {
                "name": "Data Wrangling & Time-Series with Pandas",
                "description": "Indexing, filtering, grouped aggregations, join merges, handling missing values, time-series resampling.",
                "module_name": "Module 2: Structured Data Manipulation",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Python for Data Analysis 3rd Ed. (Wes McKinney)",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Multi-Index DataFrames & Stacking Operations", "Groupby Split-Apply-Combine Engine", "Time-Series Resampling & Rolling Windows", "Handling Missing Data with Imputation Strategies"]
            },
            {
                "name": "Statistical Inference & Hypothesis Testing",
                "description": "Probability distributions, Central Limit Theorem, Student's T-Test, Chi-Square, ANOVA, p-values and confidence intervals.",
                "module_name": "Module 3: Statistical Inference & Testing",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "Wackerly, Mendenhall, Scheaffer Mathematical Statistics with Applications",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Central Limit Theorem & Sampling Distributions", "Two-Sample T-Tests & Welch's T-Test", "One-Way & Two-Way ANOVA Tests", "Type I and Type II Errors & Statistical Power"]
            },
            {
                "name": "Data Storytelling & Interactive Visual Analytics",
                "description": "Seaborn statistical plots, Matplotlib figure architecture, Plotly interactive graphics, dashboard storytelling.",
                "module_name": "Module 4: Exploratory Analysis & Storytelling",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Edward Tufte The Visual Display of Quantitative Information / Seaborn Docs",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Distribution Visualizations (KDE, Boxplots, Violins)", "Correlation Matrices & Heatmap Interpretations", "Interactive Web Visualizations with Plotly", "Dashboard Design Principles & Cognitive Load"]
            },
            {
                "name": "Columnar In-Memory Processing: DuckDB & Polars",
                "description": "Columnar Arrow memory format, vector execution engines, lightning-fast out-of-core analytics with DuckDB and Polars.",
                "module_name": "Module 5: Emerging High-Speed Data Analytics",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "VLDB 2024: DuckDB an Embeddable Analytical Database / Apache Arrow",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Apache Arrow Columnar In-Memory Standard", "Vectorized Query Execution Engine in DuckDB", "Polars Rust-Based Lazy Frame Evaluation", "Querying Parquet Files Directly with Zero Ingestion"]
            }
        ]
    },

    # 13. Cloud Computing
    {
        "name": "Cloud Computing",
        "code": "CS-405",
        "category": "Systems & Infrastructure",
        "icon_name": "Cloud",
        "description": "IaaS/PaaS/SaaS architectures, AWS/Azure/GCP core services, serverless execution, Kubernetes orchestration, and GitOps.",
        "topics": [
            {
                "name": "Cloud Architecture Models & Virtualization",
                "description": "Shared responsibility model, IaaS vs PaaS vs SaaS, Type-1/Type-2 hypervisors, VPC networking.",
                "module_name": "Module 1: Cloud Principles & Virtualization",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "NIST SP 800-145 (Cloud Definition) / AWS Well-Architected Framework",
                "last_updated_date": "2025-Q3",
                "subtopics": ["NIST Cloud Essential Characteristics", "Shared Security Responsibility Matrix", "Virtual Private Clouds (VPC) & Subnet Isolation", "Hypervisor Architecture & Hardware-Assisted Virtualization"]
            },
            {
                "name": "Cloud Compute, Storage & Auto-Scaling",
                "description": "Virtual compute instances, block storage vs object storage, horizontal auto-scaling, and load balancing.",
                "module_name": "Module 2: Scalable Compute & Storage",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "AWS Architecture Center / Google Cloud Documentation",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Elastic Compute (EC2) Instance Life Cycles", "Object Storage (S3) Consistency & Lifecycle Policies", "Application Load Balancer (ALB) Routing Rules", "Auto-Scaling Groups with Dynamic Metric Triggers"]
            },
            {
                "name": "Serverless Functions & Event-Driven Clouds",
                "description": "Function-as-a-Service (FaaS), cold starts, AWS Lambda, EventBridge, Cloud Pub/Sub, API Gateways.",
                "module_name": "Module 3: Serverless Architectures",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "Serverless Architectures (Mike Roberts) / ACM Queue",
                "last_updated_date": "2025-Q4",
                "subtopics": ["FaaS Execution Lifecycle & Cold Start Mitigation", "Event-Driven Triggers with Message Queues (SQS/SNS)", "API Gateway Throttling, Caching & Auth Integration", "Idempotency in Distributed Serverless Workflows"]
            },
            {
                "name": "Cloud Security, IAM & Identity Governance",
                "description": "Principle of least privilege, IAM policy evaluation logic, KMS encryption at rest, and secret managers.",
                "module_name": "Module 4: Cloud Identity & Governance",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "Cloud Security Alliance (CSA) Security Guidance v4 / AWS Security Best Practices",
                "last_updated_date": "2025-Q4",
                "subtopics": ["IAM Policy Evaluation Algorithm (Explicit Deny, Allow)", "Role-Based Access Control (RBAC) & AssumeRole", "Envelope Encryption with Key Management Service (KMS)", "CloudTrail & CloudWatch Security Auditing"]
            },
            {
                "name": "Kubernetes Container Orchestration & GitOps",
                "description": "Kubernetes Pods, Services, Ingress, Helm charts, declarative GitOps with ArgoCD, and serverless containers.",
                "module_name": "Module 5: Emerging Cloud Native Technologies",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "CNCF Kubernetes Documentation / ArgoCD GitOps Guides 2025",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Kubernetes Control Plane (etcd, kube-apiserver)", "Deployments, Services & Ingress Controllers", "Declarative GitOps Continuous Delivery with ArgoCD", "Serverless Containers (AWS Fargate / Google Cloud Run)"]
            }
        ]
    },

    # 14. Cybersecurity
    {
        "name": "Cybersecurity",
        "code": "CS-406",
        "category": "Software & Security",
        "icon_name": "ShieldAlert",
        "description": "CIA triad, threat modeling, cryptography (AES, RSA, ECC), OWASP Top 10 vulnerabilities, SIEM forensics, and Post-Quantum cryptography.",
        "topics": [
            {
                "name": "Threat Modeling & Security Fundamentals",
                "description": "CIA triad, STRIDE threat modeling, attack surfaces, defense-in-depth, and security policy frameworks.",
                "module_name": "Module 1: Principles & Threat Modeling",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "NIST Cybersecurity Framework 2.0 / Microsoft STRIDE Methodology",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Confidentiality, Integrity & Availability (CIA)", "STRIDE Threat Modeling Categorization", "Defense-in-Depth Layered Architecture", "Common Vulnerabilities and Exposures (CVE) & CVSS Scoring"]
            },
            {
                "name": "Applied Cryptography & Public Key Infrastructure",
                "description": "Symmetric encryption (AES-256-GCM), asymmetric keys (RSA, ECC), hashing (SHA-256), HMAC, and digital certificates.",
                "module_name": "Module 2: Cryptographic Foundations",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Ferguson, Schneier, Kohno Cryptography Engineering / NIST SP 800-57",
                "last_updated_date": "2025-Q3",
                "subtopics": ["AES-GCM Authenticated Symmetric Encryption", "Diffie-Hellman & Elliptic Curve Key Exchange", "Cryptographic Hashes & Salted PBKDF2/Argon2", "X.509 Digital Certificates & Public Key Infrastructure"]
            },
            {
                "name": "Web Application Security & OWASP Top 10",
                "description": "SQL Injection, Cross-Site Scripting (XSS), CSRF, SSRF, Broken Access Control, and secure headers.",
                "module_name": "Module 3: Application Security & Exploits",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "OWASP Top 10:2024 / PortSwigger Web Security Academy",
                "last_updated_date": "2025-Q4",
                "subtopics": ["SQL Injection Prevention with Parameterized Queries", "Stored, Reflected & DOM-Based XSS Defenses", "Server-Side Request Forgery (SSRF) Mitigations", "Content Security Policy (CSP) & Secure Cookie Flags"]
            },
            {
                "name": "Network Defense, Firewalls & SIEM Monitoring",
                "description": "Packet inspection, stateful firewalls, IDS/IPS, SIEM log analysis, and incident response lifecycles.",
                "module_name": "Module 4: Defensive Operations & Monitoring",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "NIST SP 800-61 Rev. 2 (Incident Handling) / SANS Institute",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Stateful Firewalls vs Next-Gen Application Firewalls", "Intrusion Detection Systems (Snort / Suricata)", "SIEM Log Aggregation & Correlation Rules", "Computer Security Incident Response Phases"]
            },
            {
                "name": "Post-Quantum Cryptography & AI Threat Defense",
                "description": "NIST post-quantum cryptographic standards (ML-KEM / Kyber), adversarial AI attacks, and zero-day threat defense.",
                "module_name": "Module 5: Emerging Cybersecurity Paradigms",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "NIST Post-Quantum Cryptography FIPS 203 Standards / MITRE ATLAS 2025",
                "last_updated_date": "2026-Q1",
                "subtopics": ["Lattice-Based Post-Quantum Cryptography (ML-KEM)", "Adversarial Prompt Injection & Jailbreak Defense", "Automated Security Orchestration, Automation & Response (SOAR)", "Continuous Threat Exposure Management (CTEM)"]
            }
        ]
    },

    # 15. Web Development
    {
        "name": "Web Development",
        "code": "CS-305",
        "category": "Software & Security",
        "icon_name": "Globe",
        "description": "HTML5 semantic standards, modern Tailwind CSS, modern JavaScript/TypeScript, React 18/19, Next.js App Router, and WebSockets.",
        "topics": [
            {
                "name": "Semantic HTML5, CSS Grid & Tailwind Architecture",
                "description": "Accessible semantic structure, responsive CSS Grid and Flexbox, CSS variables, and modern Tailwind utility design.",
                "module_name": "Module 1: Semantic Structure & Modern Styling",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "W3C Web Standards / MDN Web Docs / Tailwind CSS Documentation",
                "last_updated_date": "2025-Q3",
                "subtopics": ["ARIA Roles & Accessibility Standards (WCAG 2.2)", "CSS Flexbox & Two-Dimensional Grid Alignment", "Tailwind CSS Utility-First Architecture", "Fluid Typography & Responsive Breakpoints"]
            },
            {
                "name": "Modern JavaScript ES6+ & TypeScript System",
                "description": "Event loop, Promises, async/await, closures, TypeScript type guards, union types, and generics.",
                "module_name": "Module 2: JavaScript Runtime & TypeScript Typing",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "ECMA-262 ECMAScript Specification / Microsoft TypeScript Handbook",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Microtask vs Macrotask Event Loop Execution", "Promises & Async/Await Error Handling", "TypeScript Generics & Discriminated Union Types", "Type Narrowing & Custom Type Guards"]
            },
            {
                "name": "React Component Architecture & State Hooks",
                "description": "Virtual DOM reconciliation, useState, useEffect, useMemo, useCallback, custom hooks, and Context API.",
                "module_name": "Module 3: React Architecture & Reactive State",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "React.dev Official Documentation (React 18/19)",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Virtual DOM Fiber Reconciliation Engine", "State Immutability & Re-rendering Lifecycle", "Hook Rules & useEffect Dependency Synchronization", "Performance Optimization with useMemo & useCallback"]
            },
            {
                "name": "RESTful API Integration & Client-Side Caching",
                "description": "HTTP request lifecycle, JSON parsing, authentication headers, error boundaries, and TanStack Query caching.",
                "module_name": "Module 4: Client-Server Data Contracts",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "REST API Design Rulebook (Mark Masse) / TanStack Query Docs",
                "last_updated_date": "2025-Q4",
                "subtopics": ["HTTP Methods, Status Codes & Header Inspection", "JWT Token Storage & Interceptors", "Optimistic UI Updates & Cache Invalidation", "React Error Boundaries & Fallback UI"]
            },
            {
                "name": "Next.js App Router, Server Components & WebSockets",
                "description": "React Server Components (RSC), streaming SSR with Suspense, Server Actions, and real-time WebSocket communication.",
                "module_name": "Module 5: Emerging Web Architecture",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "Next.js 14/15 Architecture Guide / W3C WebSockets Standard",
                "last_updated_date": "2026-Q1",
                "subtopics": ["React Server Components (RSC) vs Client Components", "Streaming Server-Side Rendering with Suspense", "Next.js Server Actions for Secure Mutations", "Real-Time Bidirectional Communication with WebSockets"]
            }
        ]
    },

    # 16. Computer Organization and Architecture
    {
        "name": "Computer Organization and Architecture",
        "code": "CS-202",
        "category": "Core Computer Science",
        "icon_name": "Cpu",
        "description": "Digital logic, CPU datapath, Instruction Set Architecture (RISC vs CISC), pipelining hazards, cache hierarchy, and RISC-V.",
        "topics": [
            {
                "name": "Digital Logic, ALU & Number Representations",
                "description": "Boolean algebra, Karnaugh maps, combinational adders/multiplexers, sequential flip-flops, IEEE 754 float format.",
                "module_name": "Module 1: Digital Logic & Hardware Circuits",
                "order_index": 1,
                "is_emerging": False,
                "source_reference": "Mano & Ciletti Digital Design 6th Ed. / Patterson & Hennessy",
                "last_updated_date": "2025-Q2",
                "subtopics": ["Karnaugh Map Boolean Circuit Minimization", "Arithmetic Logic Unit (ALU) Adders & Shifters", "Sequential Flip-Flops & Hardware Registers", "IEEE 754 Single & Double Precision Float Specs"]
            },
            {
                "name": "Instruction Set Architecture (ISA) & CPU Datapath",
                "description": "von Neumann vs Harvard models, RISC vs CISC, instruction cycles, register files, and control unit design.",
                "module_name": "Module 2: Datapath & Instruction Sets",
                "order_index": 2,
                "is_emerging": False,
                "source_reference": "Patterson & Hennessy Computer Organization and Design: RISC-V Edition",
                "last_updated_date": "2025-Q3",
                "subtopics": ["von Neumann Stored-Program Architecture", "RISC Fixed-Length vs CISC Variable-Length Instructions", "Single-Cycle Datapath & Control Signals", "Register Files & Memory Addressing Modes"]
            },
            {
                "name": "Instruction Pipelining & Hazard Resolution",
                "description": "5-stage CPU pipeline (IF, ID, EX, MEM, WB), structural hazards, data hazards (forwarding), branch prediction.",
                "module_name": "Module 3: Pipelining & Superscalar Execution",
                "order_index": 3,
                "is_emerging": False,
                "source_reference": "Patterson & Hennessy Computer Architecture: A Quantitative Approach 6th Ed.",
                "last_updated_date": "2025-Q3",
                "subtopics": ["Classic 5-Stage RISC Pipeline Architecture", "Data Hazard Forwarding & Pipeline Stalls", "Control Hazards & Static/Dynamic Branch Prediction", "Superscalar Execution & Instruction-Level Parallelism"]
            },
            {
                "name": "Memory Hierarchy, Cache Mapping & Virtual Memory MMU",
                "description": "Direct-mapped, set-associative caches, cache hit/miss penalties, write-through vs write-back, and MMU translation.",
                "module_name": "Module 4: Cache Hierarchy & Memory Bus",
                "order_index": 4,
                "is_emerging": False,
                "source_reference": "CS:APP 3rd Ed. / Patterson & Hennessy Quantitative Approach",
                "last_updated_date": "2025-Q4",
                "subtopics": ["Direct-Mapped vs N-Way Set-Associative Caches", "Cache Write Policies (Write-Through vs Write-Back)", "Cache Replacement Algorithms (LRU, Pseudo-LRU)", "Memory Management Unit (MMU) & Address Translation"]
            },
            {
                "name": "RISC-V Open Architecture & GPU / TPU Parallel Processing",
                "description": "RISC-V open standard ISA extensions, SIMD/SIMT GPU architectures, and dedicated AI Tensor Processing Units (TPUs).",
                "module_name": "Module 5: Emerging Modern Computer Architectures",
                "order_index": 5,
                "is_emerging": True,
                "source_reference": "RISC-V International Specifications 2024 / IEEE Micro Special on AI Accelerators",
                "last_updated_date": "2026-Q1",
                "subtopics": ["RISC-V Modular ISA Extensions (RV64GC, Vector V)", "Single Instruction Multiple Threads (SIMT) GPU Model", "Tensor Processing Unit (TPU) Matrix Systolic Arrays", "Neuromorphic & Energy-Efficient Edge Compute Architectures"]
            }
        ]
    }
]

# Skills Catalog
SKILLS_CATALOG = [
    {"name": "SQL Querying", "category": "Database", "description": "Writing complex multi-table queries, aggregations, and CTEs"},
    {"name": "Database Design & Normalization", "category": "Database", "description": "Architecting 3NF schemas, constraints, and entity relationships"},
    {"name": "Query Optimization", "category": "Database", "description": "Execution plan analysis, index selection, and caching"},
    {"name": "Vector Database Architecture", "category": "Database", "description": "Managing high-dimensional vector embeddings, HNSW indexes, and pgvector"},
    {"name": "Algorithms & Optimization", "category": "Computer Science", "description": "Designing efficient algorithmic solutions with optimal Big-O"},
    {"name": "Python Programming", "category": "Programming", "description": "Idiomatic Python, OOP, typing, and standard libraries"},
    {"name": "Java & JVM Engineering", "category": "Programming", "description": "Java SE 21, JVM tuning, Spring Boot, and Virtual Threads"},
    {"name": "C Systems Programming", "category": "Programming", "description": "Low-level memory management, pointers, and POSIX system programming"},
    {"name": "Operating System Architecture", "category": "Systems", "description": "Kernel concepts, CPU scheduling, concurrency, and virtual memory"},
    {"name": "Network Protocol Analysis", "category": "Networking", "description": "Inspecting packet headers, TCP/UDP streams, and QUIC protocols"},
    {"name": "Software Architecture & Design Patterns", "category": "Software Engineering", "description": "SOLID principles, GoF patterns, microservices, and clean code"},
    {"name": "Artificial Intelligence & Heuristics", "category": "AI", "description": "Search algorithms, heuristic evaluation, and autonomous agents"},
    {"name": "Machine Learning & Predictive Modeling", "category": "Machine Learning", "description": "Supervised/unsupervised algorithms, scikit-learn, and evaluation metrics"},
    {"name": "Deep Learning & Transformers", "category": "Deep Learning", "description": "Neural network architectures, PyTorch, and Transformer self-attention"},
    {"name": "Data Analysis & Statistics", "category": "Data Science", "description": "Pandas, statistical distributions, hypothesis testing, and storytelling"},
    {"name": "Cloud Architecture & DevOps", "category": "Cloud", "description": "AWS/GCP/Azure infrastructure, Kubernetes orchestration, and CI/CD"},
    {"name": "Cybersecurity & Defensive Controls", "category": "Security", "description": "Public key crypto, OWASP vulnerability defense, and Zero Trust"},
    {"name": "Modern React & Web Engineering", "category": "Frontend", "description": "React component state, Next.js App Router, and responsive Tailwind UI"},
    {"name": "Computer Organization & Datapaths", "category": "Hardware", "description": "CPU datapath, pipelining hazards, cache memory, and RISC-V architecture"}
]

# Subject-Skill Mappings connecting subjects to industry skills and career roles
SUBJECT_SKILL_MAPPINGS = [
    # DBMS
    {
        "subject_name": "DBMS",
        "topic_name": "SQL & Relational Queries",
        "competency": "Relational Data Retrieval & Filtering",
        "skill_name": "SQL Querying",
        "career_roles": ["Database Developer", "Data Analyst", "Backend Developer"]
    },
    {
        "subject_name": "DBMS",
        "topic_name": "Database Normalization & Functional Dependencies",
        "competency": "Schema Architecture & Redundancy Reduction",
        "skill_name": "Database Design & Normalization",
        "career_roles": ["Database Developer", "Backend Developer"]
    },
    {
        "subject_name": "DBMS",
        "topic_name": "Indexing & Query Optimization",
        "competency": "Performance Tuning & Storage Efficiency",
        "skill_name": "Query Optimization",
        "career_roles": ["Database Developer", "Backend Developer"]
    },
    {
        "subject_name": "DBMS",
        "topic_name": "Vector Databases & Semantic Embeddings",
        "competency": "High-Dimensional Vector Storage & Semantic Search",
        "skill_name": "Vector Database Architecture",
        "career_roles": ["Machine Learning Engineer", "Backend Developer", "Data Scientist"]
    },
    # DSA
    {
        "subject_name": "Data Structures and Algorithms",
        "topic_name": "Asymptotic Analysis & Big-O",
        "competency": "Computational Complexity Analysis",
        "skill_name": "Algorithms & Optimization",
        "career_roles": ["Python Developer", "Backend Developer", "Machine Learning Engineer"]
    },
    {
        "subject_name": "Data Structures and Algorithms",
        "topic_name": "Graph Algorithms & Shortest Paths",
        "competency": "Network Flow & Topological Problem Solving",
        "skill_name": "Algorithms & Optimization",
        "career_roles": ["Python Developer", "Backend Developer"]
    },
    # Python
    {
        "subject_name": "Python Programming",
        "topic_name": "Python Core Syntax & Data Model",
        "competency": "Idiomatic Data Model Manipulation",
        "skill_name": "Python Programming",
        "career_roles": ["Python Developer", "Data Analyst", "Data Scientist"]
    },
    {
        "subject_name": "Python Programming",
        "topic_name": "Concurrency with AsyncIO & Multiprocessing",
        "competency": "Asynchronous High-Throughput I/O Services",
        "skill_name": "Python Programming",
        "career_roles": ["Python Developer", "Backend Developer"]
    },
    # Java
    {
        "subject_name": "Java Programming",
        "topic_name": "Java Syntax, JVM Architecture & OOP",
        "competency": "Enterprise Class Contracts & JVM Optimization",
        "skill_name": "Java & JVM Engineering",
        "career_roles": ["Backend Developer"]
    },
    # Operating Systems
    {
        "subject_name": "Operating Systems",
        "topic_name": "Concurrency, Mutexes & Deadlocks",
        "competency": "Critical Section Synchronization & Thread Safety",
        "skill_name": "Operating System Architecture",
        "career_roles": ["Backend Developer", "Cybersecurity Analyst"]
    },
    # Computer Networks
    {
        "subject_name": "Computer Networks",
        "topic_name": "Application Protocols: HTTP/2, DNS & TLS 1.3",
        "competency": "Secure Transport Protocol Engineering",
        "skill_name": "Network Protocol Analysis",
        "career_roles": ["Cybersecurity Analyst", "Backend Developer"]
    },
    # Software Engineering
    {
        "subject_name": "Software Engineering",
        "topic_name": "SOLID Principles & Gang of Four Design Patterns",
        "competency": "Maintainable Modular Software Architecture",
        "skill_name": "Software Architecture & Design Patterns",
        "career_roles": ["Backend Developer", "Web Developer", "Python Developer"]
    },
    # AI
    {
        "subject_name": "Artificial Intelligence",
        "topic_name": "Intelligent Agents & Problem-Solving Search",
        "competency": "Autonomous Problem Space Optimization",
        "skill_name": "Artificial Intelligence & Heuristics",
        "career_roles": ["Machine Learning Engineer", "Data Scientist"]
    },
    # Machine Learning
    {
        "subject_name": "Machine Learning",
        "topic_name": "Decision Trees & Gradient Boosted Ensembles",
        "competency": "Non-Linear Tabular Predictive Modeling",
        "skill_name": "Machine Learning & Predictive Modeling",
        "career_roles": ["Data Scientist", "Machine Learning Engineer"]
    },
    # Deep Learning
    {
        "subject_name": "Deep Learning",
        "topic_name": "Transformer Architecture & Self-Attention Mechanics",
        "competency": "Attention Matrix Engineering & Sequence Modeling",
        "skill_name": "Deep Learning & Transformers",
        "career_roles": ["Machine Learning Engineer", "Data Scientist"]
    },
    # Data Science
    {
        "subject_name": "Data Science",
        "topic_name": "Statistical Inference & Hypothesis Testing",
        "competency": "Rigorous Empirical Significance Verification",
        "skill_name": "Data Analysis & Statistics",
        "career_roles": ["Data Analyst", "Data Scientist"]
    },
    # Cloud Computing
    {
        "subject_name": "Cloud Computing",
        "topic_name": "Kubernetes Container Orchestration & GitOps",
        "competency": "Cloud Native Orchestration & Declarative Deployments",
        "skill_name": "Cloud Architecture & DevOps",
        "career_roles": ["Backend Developer", "Cybersecurity Analyst"]
    },
    # Cybersecurity
    {
        "subject_name": "Cybersecurity",
        "topic_name": "Web Application Security & OWASP Top 10",
        "competency": "Application Vulnerability Mitigation & Code Defense",
        "skill_name": "Cybersecurity & Defensive Controls",
        "career_roles": ["Cybersecurity Analyst", "Backend Developer"]
    },
    # Web Development
    {
        "subject_name": "Web Development",
        "topic_name": "React Component Architecture & State Hooks",
        "competency": "Declarative User Interfaces & State Synchronization",
        "skill_name": "Modern React & Web Engineering",
        "career_roles": ["Web Developer"]
    },
    # Computer Organization
    {
        "subject_name": "Computer Organization and Architecture",
        "topic_name": "Instruction Pipelining & Hazard Resolution",
        "competency": "Hardware Level Concurrency & Hazard Mitigation",
        "skill_name": "Computer Organization & Datapaths",
        "career_roles": ["Backend Developer"]
    }
]

# Role requirements mapping
CAREER_SKILL_REQUIREMENTS = {
    "Python Developer": [
        ("Python Programming", "Core", 80.0),
        ("Algorithms & Optimization", "Core", 75.0),
        ("SQL Querying", "Core", 70.0),
        ("Software Architecture & Design Patterns", "Secondary", 65.0),
        ("Operating System Architecture", "Secondary", 55.0)
    ],
    "Data Analyst": [
        ("SQL Querying", "Core", 85.0),
        ("Data Analysis & Statistics", "Core", 80.0),
        ("Python Programming", "Secondary", 70.0),
        ("Database Design & Normalization", "Secondary", 60.0)
    ],
    "Data Scientist": [
        ("Machine Learning & Predictive Modeling", "Core", 85.0),
        ("Data Analysis & Statistics", "Core", 80.0),
        ("Python Programming", "Core", 80.0),
        ("Deep Learning & Transformers", "Secondary", 70.0),
        ("SQL Querying", "Secondary", 65.0)
    ],
    "Web Developer": [
        ("Modern React & Web Engineering", "Core", 85.0),
        ("Software Architecture & Design Patterns", "Core", 75.0),
        ("Algorithms & Optimization", "Secondary", 60.0),
        ("Network Protocol Analysis", "Secondary", 55.0)
    ],
    "Backend Developer": [
        ("SQL Querying", "Core", 80.0),
        ("Database Design & Normalization", "Core", 75.0),
        ("Software Architecture & Design Patterns", "Core", 75.0),
        ("Operating System Architecture", "Core", 70.0),
        ("Cloud Architecture & DevOps", "Secondary", 65.0),
        ("Cybersecurity & Defensive Controls", "Secondary", 60.0)
    ],
    "Database Developer": [
        ("SQL Querying", "Core", 90.0),
        ("Database Design & Normalization", "Core", 85.0),
        ("Query Optimization", "Core", 85.0),
        ("Vector Database Architecture", "Secondary", 70.0),
        ("Operating System Architecture", "Secondary", 60.0)
    ],
    "Machine Learning Engineer": [
        ("Deep Learning & Transformers", "Core", 85.0),
        ("Machine Learning & Predictive Modeling", "Core", 85.0),
        ("Python Programming", "Core", 80.0),
        ("Algorithms & Optimization", "Core", 75.0),
        ("Vector Database Architecture", "Secondary", 70.0),
        ("Cloud Architecture & DevOps", "Secondary", 65.0)
    ],
    "Cybersecurity Analyst": [
        ("Cybersecurity & Defensive Controls", "Core", 85.0),
        ("Network Protocol Analysis", "Core", 85.0),
        ("Operating System Architecture", "Core", 75.0),
        ("Cloud Architecture & DevOps", "Secondary", 65.0),
        ("Python Programming", "Secondary", 60.0)
    ],
    "Cloud Solutions Architect": [
        ("Cloud Architecture & DevOps", "Core", 85.0),
        ("Operating System Architecture", "Core", 80.0),
        ("Network Protocol Analysis", "Core", 75.0),
        ("Software Architecture & Design Patterns", "Secondary", 70.0),
        ("Cybersecurity & Defensive Controls", "Secondary", 65.0),
        ("Python Programming", "Secondary", 60.0)
    ],
    "AI Engineer": [
        ("Deep Learning & Transformers", "Core", 85.0),
        ("Vector Database Architecture", "Core", 80.0),
        ("Python Programming", "Core", 80.0),
        ("Machine Learning & Predictive Modeling", "Core", 75.0),
        ("Algorithms & Optimization", "Secondary", 70.0),
        ("Cloud Architecture & DevOps", "Secondary", 65.0)
    ]
}

CAREER_PROJECTS = [
    {
        "career_role_title": "Python Developer",
        "title": "Scalable Async Task Processing Microservice",
        "objective": "Build a high-throughput background job processing engine with FastAPI, Redis Streams, and asynchronous worker pools.",
        "difficulty": "Intermediate",
        "required_skills": ["Python Programming", "Algorithms & Optimization"],
        "tools": ["Python 3.11", "FastAPI", "Redis Streams", "Docker", "Pytest"],
        "steps": [
            "Initialize FastAPI async project skeleton with pydantic schemas and dependency injection.",
            "Configure Redis connection pool with stream consumers and consumer group acknowledgments.",
            "Implement exponential backoff retry mechanisms and dead-letter queue routing for failed jobs.",
            "Write comprehensive asynchronous unit and integration test suite using pytest-asyncio."
        ],
        "expected_outcome": "A production-ready microservice capable of executing 5,000 concurrent async jobs with zero message loss and real-time status reporting.",
        "competency_focus": "Asynchronous Concurrency & System Reliability"
    },
    {
        "career_role_title": "Data Analyst",
        "title": "Executive Business Intelligence & Cohort Retention Dashboard",
        "objective": "Cleanse real-world transactional datasets, perform cohort retention analysis, and build an automated reporting pipeline.",
        "difficulty": "Beginner",
        "required_skills": ["Data Analysis & Statistics", "SQL Querying"],
        "tools": ["Python", "Pandas", "PostgreSQL", "Metabase / Streamlit", "Seaborn"],
        "steps": [
            "Import and clean 100,000+ transactional records, handling missing values and outlier anomalies.",
            "Construct SQL window queries to calculate monthly customer cohort retention curves and LTV.",
            "Perform statistical hypothesis testing on user churn factors using scipy.stats.",
            "Publish an interactive multi-filter dashboard with executive KPI cards and automated trend summaries."
        ],
        "expected_outcome": "A fully functional analytical dashboard uncovering churn patterns with automated monthly metric generation.",
        "competency_focus": "Data Wrangling, Statistical Inference & Business Storytelling"
    },
    {
        "career_role_title": "Data Scientist",
        "title": "Customer Churn Prediction Engine with Model Explainability",
        "objective": "Develop, validate, and deploy an end-to-end classification pipeline featuring XGBoost, SHAP feature importance, and REST inference.",
        "difficulty": "Advanced",
        "required_skills": ["Machine Learning & Predictive Modeling", "Python Programming", "Data Analysis & Statistics"],
        "tools": ["Scikit-learn", "XGBoost", "SHAP", "FastAPI", "MLflow"],
        "steps": [
            "Perform exploratory data analysis and engineer domain features (recency, frequency, monetary ratios).",
            "Train baseline Logistic Regression and tuned XGBoost models with 5-fold cross-validation.",
            "Compute SHAP values to explain individual prediction decisions transparently.",
            "Wrap inference model in a lightweight FastAPI service with request validation and latency monitoring."
        ],
        "expected_outcome": "A predictive model achieving >88% ROC-AUC with explainable AI reports for every inference call.",
        "competency_focus": "Predictive Modeling, Model Explainability & Production Inference"
    },
    {
        "career_role_title": "Web Developer",
        "title": "Real-Time Collaborative Knowledge Canvas",
        "objective": "Develop a responsive, accessible Next.js web application with WebSocket synchronization, optimistic UI updates, and Dark Mode design system.",
        "difficulty": "Intermediate",
        "required_skills": ["Modern React & Web Engineering", "Software Architecture & Design Patterns"],
        "tools": ["Next.js 14", "React", "TypeScript", "Tailwind CSS", "WebSockets / Socket.io"],
        "steps": [
            "Architect the component tree with React 18 server and client components, avoiding unnecessary re-renders.",
            "Implement a dark-first design system using Tailwind CSS with WCAG AAA contrast compliance.",
            "Integrate WebSocket connection with reconnection logic, cursor presence, and operational transformation.",
            "Add offline support and local storage caching for draft auto-saving."
        ],
        "expected_outcome": "A fluid collaborative document editor supporting concurrent multi-user editing with sub-50ms latency.",
        "competency_focus": "Full-Stack Web Engineering, Component Architecture & Real-Time Sync"
    },
    {
        "career_role_title": "Backend Developer",
        "title": "Distributed E-Commerce Order Management Architecture",
        "objective": "Architect a fault-tolerant order dispatch system with distributed ACID transactions (Saga Pattern), JWT authentication, and Docker deployment.",
        "difficulty": "Advanced",
        "required_skills": ["SQL Querying", "Database Design & Normalization", "Software Architecture & Design Patterns"],
        "tools": ["FastAPI / Go", "PostgreSQL", "RabbitMQ", "Docker Compose", "Alembic"],
        "steps": [
            "Design relational schemas in 3NF with foreign keys, check constraints, and migration scripts.",
            "Implement JWT RBAC authentication with refresh token rotation and secure cookie handling.",
            "Construct Choreographed Saga pattern with RabbitMQ events for inventory, payment, and shipping.",
            "Profile and tune database queries using EXPLAIN ANALYZE to achieve sub-10ms p95 latencies."
        ],
        "expected_outcome": "A fault-tolerant distributed order service that cleanly handles partial system failures and guarantees eventual data consistency.",
        "competency_focus": "Distributed Systems, Transactional Guarantees & Scalability"
    },
    {
        "career_role_title": "Database Developer",
        "title": "High-Volume Financial Ledger with Partitioning & Audit Triggers",
        "objective": "Design normalized 3NF schemas, implement table partitioning by date range, write row-level audit triggers, and optimize p99 query latencies with compound B-Trees.",
        "difficulty": "Advanced",
        "required_skills": ["SQL Querying", "Database Design & Normalization", "Query Optimization"],
        "tools": ["PostgreSQL", "PL/pgSQL", "pg_stat_statements", "EXPLAIN ANALYZE", "Redis"],
        "steps": [
            "Construct a double-entry accounting schema with declarative range partitioning across fiscal quarters.",
            "Write PL/pgSQL triggers to automatically enforce non-repudiation and populate immutable audit tables.",
            "Design compound B-Tree, Hash, and BRIN indexes to optimize range scans on 10M+ row tables.",
            "Benchmarking and load testing under 1,000 transactions per second using pgbench."
        ],
        "expected_outcome": "An enterprise financial database engine maintaining sub-5ms query times with complete audit trail integrity.",
        "competency_focus": "Database Normalization, Query Tuning & Storage Architecture"
    },
    {
        "career_role_title": "Machine Learning Engineer",
        "title": "Enterprise Vector Search & RAG Retrieval Microservice",
        "objective": "Build an automated document indexing, semantic chunking, and low-latency vector similarity retrieval pipeline with Qdrant and FastAPI.",
        "difficulty": "Advanced",
        "required_skills": ["Deep Learning & Transformers", "Machine Learning & Predictive Modeling", "Vector Database Architecture"],
        "tools": ["Python", "PyTorch", "HuggingFace Transformers", "Qdrant", "FastAPI"],
        "steps": [
            "Implement recursive semantic text chunker preserving markdown structural boundaries.",
            "Generate dense embeddings using open-source models (e.g. all-MiniLM-L6-v2) with GPU acceleration.",
            "Store and index vectors in Qdrant with HNSW graph indexing for sub-15ms approximate nearest neighbors.",
            "Implement hybrid reranking combining dense cosine similarity with BM25 keyword matching."
        ],
        "expected_outcome": "A production-grade RAG retrieval microservice delivering 95%+ precision on technical documentation queries.",
        "competency_focus": "Vector Embeddings, Neural Search & Production MLOps"
    },
    {
        "career_role_title": "Cybersecurity Analyst",
        "title": "Automated Network Threat Detection & SIEM Vulnerability Scanner",
        "objective": "Implement packet inspection and log analysis pipelines to detect SQL injection, brute force attempts, and anomalous tokens with automated alerting.",
        "difficulty": "Intermediate",
        "required_skills": ["Cybersecurity & Defensive Controls", "Network Protocol Analysis", "Operating System Architecture"],
        "tools": ["Python", "Scapy", "Wireshark / PCAP", "Zeek", "OWASP ZAP"],
        "steps": [
            "Develop a packet sniffer with Scapy to identify unencrypted credentials and anomalous TCP handshake patterns.",
            "Parse web server access logs using regex patterns to flag SQL injection and Path Traversal attack vectors.",
            "Write automated alerting scripts dispatching incident notifications with source IP, payload, and threat severity.",
            "Conduct automated vulnerability assessment against staging servers and compile executive audit report."
        ],
        "expected_outcome": "A proactive security monitoring utility capable of detecting and classifying OWASP Top 10 exploits in real time.",
        "competency_focus": "Threat Hunting, Network Forensics & Defensive Hardening"
    },
    {
        "career_role_title": "Cloud Solutions Architect",
        "title": "Multi-Region Kubernetes Microservices & GitOps Platform",
        "objective": "Architect high-availability infrastructure with Terraform, deploy resilient microservices on Kubernetes, and enforce zero-trust network policies.",
        "difficulty": "Advanced",
        "required_skills": ["Cloud Architecture & DevOps", "Operating System Architecture", "Network Protocol Analysis"],
        "tools": ["Kubernetes", "Terraform", "Docker", "ArgoCD", "Prometheus & Grafana"],
        "steps": [
            "Write modular Terraform declarations provisioning multi-AZ VPC, subnets, and Kubernetes clusters.",
            "Configure ingress controllers with automated TLS certificate issuance and rate-limiting middleware.",
            "Deploy GitOps automated delivery pipeline using ArgoCD syncing application manifests from Git.",
            "Implement Prometheus metrics collection and Grafana dashboards tracking cluster SLOs and latency."
        ],
        "expected_outcome": "A resilient multi-region cloud cluster demonstrating automated failover and 99.99% availability.",
        "competency_focus": "Cloud Orchestration, Infrastructure as Code & Reliability Engineering"
    },
    {
        "career_role_title": "AI Engineer",
        "title": "Autonomous Multi-Agent Workflow Engine with Hybrid Vector Retrieval",
        "objective": "Build an enterprise LLM agent orchestrator featuring tool execution, persistent conversational memory, and hybrid dense/sparse vector retrieval.",
        "difficulty": "Advanced",
        "required_skills": ["Deep Learning & Transformers", "Vector Database Architecture", "Python Programming"],
        "tools": ["Python 3.11", "LangChain / LangGraph", "Qdrant", "FastAPI", "OpenAI / Gemini"],
        "steps": [
            "Implement an iterative ReAct reasoning loop with dynamic tool dispatching and guardrails.",
            "Build a hybrid RAG pipeline combining BM25 keyword search with dense vector similarity and cross-encoder reranking.",
            "Implement persistent session state caching using Redis and asynchronous streaming tokens over Server-Sent Events.",
            "Evaluate agent precision and hallucination rates using automated synthetic benchmark suites."
        ],
        "expected_outcome": "An intelligent multi-agent platform capable of decomposing complex academic and industry goals with sub-second token latency.",
        "competency_focus": "Agentic AI Architectures, Neural Retrieval & LLM Systems"
    }
]

CAREER_PATHWAYS = [
    {
        "from_role": "Python Developer",
        "to_role": "Backend Developer",
        "transition_difficulty": "Smooth",
        "bridge_skills": ["Database Design & Normalization", "Software Architecture & Design Patterns", "SQL Querying"],
        "guidance": "You already possess strong Python fundamentals. Transition by building distributed APIs with FastAPI/PostgreSQL and mastering ACID transaction guarantees."
    },
    {
        "from_role": "Python Developer",
        "to_role": "Data Scientist",
        "transition_difficulty": "Moderate",
        "bridge_skills": ["Machine Learning & Predictive Modeling", "Data Analysis & Statistics", "Deep Learning & Transformers"],
        "guidance": "Leverage your Python coding proficiency to learn linear algebra, probability, Scikit-learn, and feature engineering workflows."
    },
    {
        "from_role": "Data Analyst",
        "to_role": "Data Scientist",
        "transition_difficulty": "Moderate",
        "bridge_skills": ["Machine Learning & Predictive Modeling", "Python Programming", "Deep Learning & Transformers"],
        "guidance": "Expand your existing SQL and analytical skills into predictive modeling, algorithmic thinking, and automated ML pipelines."
    },
    {
        "from_role": "Web Developer",
        "to_role": "Backend Developer",
        "transition_difficulty": "Moderate",
        "bridge_skills": ["SQL Querying", "Database Design & Normalization", "Operating System Architecture"],
        "guidance": "Transition from frontend component state to server-side persistence, SQL query optimization, database locking, and background worker queues."
    },
    {
        "from_role": "Database Developer",
        "to_role": "Backend Developer",
        "transition_difficulty": "Smooth",
        "bridge_skills": ["Software Architecture & Design Patterns", "Python Programming", "Cloud Architecture & DevOps"],
        "guidance": "Your deep data and SQL mastery gives you a huge advantage. Learn REST API frameworks, microservice orchestration, and containerized deployments."
    },
    {
        "from_role": "Backend Developer",
        "to_role": "Machine Learning Engineer",
        "transition_difficulty": "Challenging",
        "bridge_skills": ["Machine Learning & Predictive Modeling", "Deep Learning & Transformers", "Vector Database Architecture"],
        "guidance": "Complement your microservice and scalability skills with PyTorch, model quantization, vector retrieval, and production MLOps."
    },
    {
        "from_role": "Backend Developer",
        "to_role": "Cloud Solutions Architect",
        "transition_difficulty": "Smooth",
        "bridge_skills": ["Cloud Architecture & DevOps", "Network Protocol Analysis"],
        "guidance": "Leverage your server-side foundation to master Kubernetes cluster orchestration, Terraform infrastructure-as-code, and multi-region cloud security."
    },
    {
        "from_role": "Machine Learning Engineer",
        "to_role": "AI Engineer",
        "transition_difficulty": "Smooth",
        "bridge_skills": ["Vector Database Architecture", "Cloud Architecture & DevOps"],
        "guidance": "Transition from training custom models to building end-to-end agentic workflows, low-latency hybrid RAG pipelines, and production LLM orchestration."
    }
]
