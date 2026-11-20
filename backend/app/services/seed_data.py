"""
Academic-to-Industry Taxonomy & Seed Dataset for EduPath AI.
Maps Academic Subjects -> Topics -> Industry Competencies -> Skills -> Career Roles.
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
    }
]

SUBJECTS_AND_TOPICS = [
    {
        "name": "Database Management Systems",
        "code": "CS-301",
        "description": "Relational algebra, SQL, normalization, transactions, ACID properties, indexing, and storage engines.",
        "topics": [
            {"name": "SQL & Relational Queries", "description": "SELECT, JOIN, Aggregations, Subqueries, CTEs", "order_index": 1},
            {"name": "Database Normalization", "description": "1NF, 2NF, 3NF, BCNF, functional dependencies", "order_index": 2},
            {"name": "Table Joins & Query Plans", "description": "Inner, outer, cross joins, query execution plans", "order_index": 3},
            {"name": "Indexing & Query Optimization", "description": "B-Trees, Hash indexes, explain analyze, index selectivity", "order_index": 4},
            {"name": "Transactions & ACID Properties", "description": "Atomicity, Consistency, Isolation, Durability, concurrency control", "order_index": 5}
        ]
    },
    {
        "name": "Data Structures & Algorithms",
        "code": "CS-201",
        "description": "Linear and non-linear data structures, asymptotic analysis, sorting, searching, and algorithmic paradigms.",
        "topics": [
            {"name": "Arrays & Hashing", "description": "Hash tables, collision resolution, array manipulations", "order_index": 1},
            {"name": "Trees & Binary Search Trees", "description": "Tree traversals, BST operations, balancing concepts", "order_index": 2},
            {"name": "Graph Algorithms", "description": "BFS, DFS, Dijkstra, topological sort, MST", "order_index": 3},
            {"name": "Dynamic Programming", "description": "Memoization, tabulation, optimal substructure", "order_index": 4},
            {"name": "Asymptotic Analysis & Big-O", "description": "Time and space complexity bounds", "order_index": 5}
        ]
    },
    {
        "name": "Operating Systems & Systems Architecture",
        "code": "CS-302",
        "description": "Processes, threads, CPU scheduling, synchronization, memory management, and file systems.",
        "topics": [
            {"name": "Process Management & Scheduling", "description": "PCB, context switching, CPU scheduling algorithms", "order_index": 1},
            {"name": "Concurrency & Mutex Locks", "description": "Race conditions, semaphores, deadlocks, atomic operations", "order_index": 2},
            {"name": "Memory Management & Paging", "description": "Virtual memory, TLB, page replacement algorithms", "order_index": 3},
            {"name": "File Systems & I/O", "description": "Inodes, file allocation tables, asynchronous I/O", "order_index": 4}
        ]
    },
    {
        "name": "Computer Networks & Security",
        "code": "CS-401",
        "description": "OSI and TCP/IP stack, routing protocols, transport layer, TLS/HTTPS, authentication, and threat analysis.",
        "topics": [
            {"name": "TCP/IP & Network Layers", "description": "IP addressing, subnetting, TCP 3-way handshake, UDP", "order_index": 1},
            {"name": "HTTP/HTTPS & Web Protocols", "description": "HTTP methods, headers, status codes, SSL/TLS handshake", "order_index": 2},
            {"name": "Network Security & Firewalls", "description": "Port scanning, firewalls, IDS/IPS, DDoS mitigation", "order_index": 3},
            {"name": "Authentication & Cryptography", "description": "Symmetric vs asymmetric keys, hashing, JWT, OAuth", "order_index": 4}
        ]
    },
    {
        "name": "Modern Web Engineering",
        "code": "CS-305",
        "description": "Client-server architecture, modern JavaScript/TypeScript, React state management, and REST APIs.",
        "topics": [
            {"name": "DOM Manipulation & Modern JavaScript", "description": "ES6+, async/await, event loop, closures", "order_index": 1},
            {"name": "React Component Architecture", "description": "JSX, hooks, state lifecycle, virtual DOM", "order_index": 2},
            {"name": "RESTful API Integration", "description": "CRUD operations, JSON serialization, HTTP status codes", "order_index": 3},
            {"name": "State Management & Responsive Design", "description": "Tailwind CSS, global state, accessible UI", "order_index": 4}
        ]
    },
    {
        "name": "Machine Learning Fundamentals",
        "code": "CS-405",
        "description": "Supervised and unsupervised learning, loss functions, gradient descent, model evaluation, and feature engineering.",
        "topics": [
            {"name": "Supervised Learning Algorithms", "description": "Linear regression, logistic regression, decision trees", "order_index": 1},
            {"name": "Model Evaluation & Validation", "description": "Confusion matrix, precision, recall, F1, ROC-AUC, cross-validation", "order_index": 2},
            {"name": "Feature Engineering & Preprocessing", "description": "Normalization, categorical encoding, handling missing data", "order_index": 3},
            {"name": "Neural Networks & Deep Learning", "description": "Backpropagation, activation functions, CNNs, transformers", "order_index": 4}
        ]
    }
]

SKILLS_CATALOG = [
    {"name": "SQL Querying", "category": "Database", "description": "Writing complex multi-table queries, aggregations, and CTEs"},
    {"name": "Database Design & Normalization", "category": "Database", "description": "Architecting 3NF schemas, constraints, and entity relationships"},
    {"name": "Query Optimization", "category": "Database", "description": "Execution plan analysis, index selection, and caching"},
    {"name": "Data Management & ETL", "category": "Data Engineering", "description": "Extracting, transforming, and loading structured datasets"},
    {"name": "Python Programming", "category": "Programming", "description": "Idiomatic Python, OOP, typing, and standard libraries"},
    {"name": "Algorithms & Optimization", "category": "Computer Science", "description": "Designing efficient algorithmic solutions with optimal Big-O"},
    {"name": "Data Analysis & Visualization", "category": "Data Science", "description": "Pandas, statistical distributions, chart interpretation"},
    {"name": "Predictive Modeling", "category": "Machine Learning", "description": "Training scikit-learn classifiers, regressors, and pipelines"},
    {"name": "Deep Learning Frameworks", "category": "Machine Learning", "description": "PyTorch, TensorFlow, neural network fine-tuning"},
    {"name": "REST API Architecture", "category": "Backend", "description": "Designing robust, authenticated, modular HTTP REST services"},
    {"name": "System Concurrency & Multithreading", "category": "Systems", "description": "Async I/O, thread safety, locks, and task scheduling"},
    {"name": "Modern React & TypeScript", "category": "Frontend", "description": "Building interactive single-page applications with TypeScript"},
    {"name": "UI/UX & Responsive Design", "category": "Frontend", "description": "Tailwind CSS, component modularity, accessibility standards"},
    {"name": "Network Protocol Analysis", "category": "Security", "description": "Inspecting packet headers, TCP/UDP streams, and latency"},
    {"name": "Security & Cryptography", "category": "Security", "description": "Public key crypto, token authentication, vulnerability triage"}
]

# Structured Academic Subject -> Topic -> Competency -> Skill -> Career Role Mappings
SUBJECT_SKILL_MAPPINGS = [
    # DBMS
    {
        "subject_name": "Database Management Systems",
        "topic_name": "SQL & Relational Queries",
        "competency": "Relational Data Retrieval & Filtering",
        "skill_name": "SQL Querying",
        "career_roles": ["Database Developer", "Data Analyst", "Backend Developer"]
    },
    {
        "subject_name": "Database Management Systems",
        "topic_name": "Database Normalization",
        "competency": "Schema Architecture & Redundancy Reduction",
        "skill_name": "Database Design & Normalization",
        "career_roles": ["Database Developer", "Backend Developer"]
    },
    {
        "subject_name": "Database Management Systems",
        "topic_name": "Indexing & Query Optimization",
        "competency": "Performance Tuning & Storage Efficiency",
        "skill_name": "Query Optimization",
        "career_roles": ["Database Developer", "Backend Developer"]
    },
    {
        "subject_name": "Database Management Systems",
        "topic_name": "Transactions & ACID Properties",
        "competency": "Data Integrity & Concurrency Control",
        "skill_name": "Database Design & Normalization",
        "career_roles": ["Database Developer", "Backend Developer"]
    },
    # DSA
    {
        "subject_name": "Data Structures & Algorithms",
        "topic_name": "Arrays & Hashing",
        "competency": "Memory Efficiency & Fast Lookups",
        "skill_name": "Algorithms & Optimization",
        "career_roles": ["Python Developer", "Backend Developer", "Machine Learning Engineer"]
    },
    {
        "subject_name": "Data Structures & Algorithms",
        "topic_name": "Dynamic Programming",
        "competency": "Optimal Substructure & Algorithmic Problem Solving",
        "skill_name": "Algorithms & Optimization",
        "career_roles": ["Python Developer", "Backend Developer", "Machine Learning Engineer"]
    },
    # Web Engineering
    {
        "subject_name": "Modern Web Engineering",
        "topic_name": "React Component Architecture",
        "competency": "Declarative UI & State Synchronization",
        "skill_name": "Modern React & TypeScript",
        "career_roles": ["Web Developer"]
    },
    {
        "subject_name": "Modern Web Engineering",
        "topic_name": "RESTful API Integration",
        "competency": "Client-Server Contract Implementation",
        "skill_name": "REST API Architecture",
        "career_roles": ["Web Developer", "Backend Developer", "Python Developer"]
    },
    {
        "subject_name": "Modern Web Engineering",
        "topic_name": "State Management & Responsive Design",
        "competency": "User Interface Usability & Layout",
        "skill_name": "UI/UX & Responsive Design",
        "career_roles": ["Web Developer"]
    },
    # Machine Learning
    {
        "subject_name": "Machine Learning Fundamentals",
        "topic_name": "Supervised Learning Algorithms",
        "competency": "Statistical Learning & Regression/Classification",
        "skill_name": "Predictive Modeling",
        "career_roles": ["Data Scientist", "Machine Learning Engineer"]
    },
    {
        "subject_name": "Machine Learning Fundamentals",
        "topic_name": "Feature Engineering & Preprocessing",
        "competency": "Data Cleaning & Vector Transformation",
        "skill_name": "Data Analysis & Visualization",
        "career_roles": ["Data Analyst", "Data Scientist", "Machine Learning Engineer"]
    },
    {
        "subject_name": "Machine Learning Fundamentals",
        "topic_name": "Neural Networks & Deep Learning",
        "competency": "Deep Architecture Training & Gradient Descent",
        "skill_name": "Deep Learning Frameworks",
        "career_roles": ["Machine Learning Engineer", "Data Scientist"]
    },
    # Networks & Security
    {
        "subject_name": "Computer Networks & Security",
        "topic_name": "Authentication & Cryptography",
        "competency": "Identity Management & Secure Channel Encryption",
        "skill_name": "Security & Cryptography",
        "career_roles": ["Cybersecurity Analyst", "Backend Developer"]
    },
    {
        "subject_name": "Computer Networks & Security",
        "topic_name": "Network Security & Firewalls",
        "competency": "Threat Surface Mitigation & Packet Inspection",
        "skill_name": "Network Protocol Analysis",
        "career_roles": ["Cybersecurity Analyst"]
    }
]

# Role requirements mapping
CAREER_SKILL_REQUIREMENTS = {
    "Python Developer": [
        ("Python Programming", "Core", 75.0),
        ("REST API Architecture", "Core", 70.0),
        ("Algorithms & Optimization", "Core", 65.0),
        ("SQL Querying", "Secondary", 60.0),
        ("System Concurrency & Multithreading", "Secondary", 55.0)
    ],
    "Data Analyst": [
        ("SQL Querying", "Core", 80.0),
        ("Data Analysis & Visualization", "Core", 75.0),
        ("Data Management & ETL", "Core", 70.0),
        ("Python Programming", "Secondary", 60.0),
        ("Database Design & Normalization", "Secondary", 55.0)
    ],
    "Data Scientist": [
        ("Predictive Modeling", "Core", 80.0),
        ("Data Analysis & Visualization", "Core", 75.0),
        ("Python Programming", "Core", 75.0),
        ("SQL Querying", "Secondary", 65.0),
        ("Deep Learning Frameworks", "Secondary", 60.0)
    ],
    "Web Developer": [
        ("Modern React & TypeScript", "Core", 80.0),
        ("UI/UX & Responsive Design", "Core", 75.0),
        ("REST API Architecture", "Core", 65.0),
        ("Algorithms & Optimization", "Secondary", 50.0)
    ],
    "Backend Developer": [
        ("REST API Architecture", "Core", 80.0),
        ("SQL Querying", "Core", 75.0),
        ("Database Design & Normalization", "Core", 70.0),
        ("System Concurrency & Multithreading", "Core", 65.0),
        ("Security & Cryptography", "Secondary", 60.0),
        ("Query Optimization", "Secondary", 60.0)
    ],
    "Database Developer": [
        ("SQL Querying", "Core", 85.0),
        ("Database Design & Normalization", "Core", 85.0),
        ("Query Optimization", "Core", 80.0),
        ("Data Management & ETL", "Core", 70.0),
        ("REST API Architecture", "Secondary", 50.0)
    ],
    "Machine Learning Engineer": [
        ("Deep Learning Frameworks", "Core", 80.0),
        ("Predictive Modeling", "Core", 80.0),
        ("Python Programming", "Core", 80.0),
        ("Algorithms & Optimization", "Core", 70.0),
        ("Data Management & ETL", "Secondary", 65.0)
    ],
    "Cybersecurity Analyst": [
        ("Security & Cryptography", "Core", 85.0),
        ("Network Protocol Analysis", "Core", 80.0),
        ("REST API Architecture", "Secondary", 60.0),
        ("System Concurrency & Multithreading", "Secondary", 60.0),
        ("Python Programming", "Secondary", 55.0)
    ]
}
