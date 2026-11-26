"""
EduPath AI - Adaptive Quiz Generator Service.
Synthesizes multiple-choice questions with balanced distractors, normalized answer keys,
and in-depth pedagogical explanations across varying difficulty tiers.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from app.services.ai.provider import llm_provider

logger = logging.getLogger("edupath.ai.quiz_generator")

# Topic-specific pedagogical knowledge banks for deterministic offline generation
CURRICULUM_QUESTION_BANKS: Dict[str, List[Dict[str, Any]]] = {
    "dsa": [
        {
            "question_text": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree (BST)?",
            "options": ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
            "correct_answer": "O(n)",
            "explanation": "When an unbalanced BST degenerates into a linear linked list (e.g., when elements are inserted in sorted order), searching requires traversing all n elements, yielding O(n) worst-case time complexity."
        },
        {
            "question_text": "Which data structure guarantees O(1) average-time complexity for key insertions and lookups?",
            "options": ["Hash Table", "Binary Search Tree", "Linked List", "Min Heap"],
            "correct_answer": "Hash Table",
            "explanation": "A Hash Table maps keys to bucket indices using a hash function, providing O(1) expected constant time for insertions and lookups assuming uniform distribution."
        },
        {
            "question_text": "What algorithm design paradigm does Dijkstra's shortest-path algorithm employ?",
            "options": ["Greedy Algorithm", "Dynamic Programming", "Divide and Conquer", "Backtracking"],
            "correct_answer": "Greedy Algorithm",
            "explanation": "Dijkstra's algorithm is a greedy algorithm that selects the unvisited vertex with the smallest tentative distance at each step."
        },
        {
            "question_text": "Which sorting algorithm maintains stability and guarantees O(n log n) worst-case time complexity?",
            "options": ["Merge Sort", "Quick Sort", "Heap Sort", "Selection Sort"],
            "correct_answer": "Merge Sort",
            "explanation": "Merge Sort guarantees O(n log n) time in all cases (best, average, worst) and preserves the relative order of duplicate elements, making it stable."
        },
        {
            "question_text": "In a max-heap with n elements, what is the time complexity of extracting the maximum root element?",
            "options": ["O(log n)", "O(1)", "O(n)", "O(n log n)"],
            "correct_answer": "O(log n)",
            "explanation": "Extracting the maximum requires replacing the root with the last leaf and performing sift-down (heapify), which traverses the height of the tree in O(log n) time."
        }
    ],
    "dbms": [
        {
            "question_text": "Which ACID property guarantees that a transaction either executes entirely or leaves the database unchanged?",
            "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
            "correct_answer": "Atomicity",
            "explanation": "Atomicity requires that all operations in a transaction succeed together or are completely rolled back upon error ('all-or-nothing')."
        },
        {
            "question_text": "What type of index structure is most widely used in relational databases for range queries?",
            "options": ["B+ Tree", "Hash Index", "Bitmap Index", "Inverted Index"],
            "correct_answer": "B+ Tree",
            "explanation": "B+ Trees store all records in leaf nodes connected by sequential pointers, making them exceptionally fast for both point lookups and range scans."
        },
        {
            "question_text": "In relational database normalization, what dependency does Third Normal Form (3NF) strictly eliminate?",
            "options": ["Transitive Dependencies", "Partial Dependencies", "Multivalued Dependencies", "Cyclic Dependencies"],
            "correct_answer": "Transitive Dependencies",
            "explanation": "3NF requires the relation to be in 2NF and ensures that no non-prime attribute is transitively dependent on the primary key."
        },
        {
            "question_text": "What isolation level prevents dirty reads, non-repeatable reads, and phantom reads?",
            "options": ["Serializable", "Repeatable Read", "Read Committed", "Read Uncommitted"],
            "correct_answer": "Serializable",
            "explanation": "Serializable is the highest ANSI SQL isolation level, executing transactions with the equivalent outcome of a strictly sequential execution."
        },
        {
            "question_text": "What is the primary operational purpose of the Database Write-Ahead Logging (WAL) protocol?",
            "options": ["Ensuring Durability and Crash Recovery", "Compressing Table Partitions", "Eliminating Index Fragmentation", "Encrypting Sensitive Columns"],
            "correct_answer": "Ensuring Durability and Crash Recovery",
            "explanation": "WAL guarantees that changes are recorded to non-volatile disk logs before table pages are updated in buffer cache, guaranteeing durability during sudden crashes."
        }
    ],
    "os": [
        {
            "question_text": "Which scheduling algorithm is non-preemptive and selects the process with the smallest CPU burst time?",
            "options": ["Shortest Job First (SJF)", "Round Robin (RR)", "Priority Scheduling", "Multilevel Feedback Queue"],
            "correct_answer": "Shortest Job First (SJF)",
            "explanation": "Non-preemptive Shortest Job First schedules the process with the shortest estimated execution time, achieving minimal average waiting time."
        },
        {
            "question_text": "Which condition is NOT one of Coffman's four necessary conditions for a deadlock to occur?",
            "options": ["Preemption Allowed", "Mutual Exclusion", "Hold and Wait", "Circular Wait"],
            "correct_answer": "Preemption Allowed",
            "explanation": "Deadlock requires 'No Preemption' (resources cannot be forcibly confiscated). If preemption is allowed, deadlocks can be broken."
        },
        {
            "question_text": "What happens during a Translation Lookaside Buffer (TLB) miss in virtual memory architectures?",
            "options": ["The MMU performs a multi-level page table walk in main memory", "A kernel panic is triggered immediately", "The page is evicted to swap disk storage", "All TLB registers are flushed"],
            "correct_answer": "The MMU performs a multi-level page table walk in main memory",
            "explanation": "When the virtual page translation is not cached in the hardware TLB, the Memory Management Unit (or OS) must walk the in-memory page tables to resolve the physical address."
        },
        {
            "question_text": "What is the primary difference between a process and a thread in modern operating systems?",
            "options": ["Threads in the same process share the virtual address space and heap", "Threads have completely independent memory address spaces", "Processes share a single execution stack", "Threads cannot execute concurrently"],
            "correct_answer": "Threads in the same process share the virtual address space and heap",
            "explanation": "Threads share the text, data, and heap segments of their parent process while retaining their own program counters, registers, and execution stacks."
        },
        {
            "question_text": "What operating system mechanism prevents user programs from directly accessing critical hardware and kernel memory?",
            "options": ["Dual-Mode CPU Execution (Kernel vs User Mode)", "Garbage Collection Cycles", "Virtual Machine Monitors", "Dynamic Link Libraries"],
            "correct_answer": "Dual-Mode CPU Execution (Kernel vs User Mode)",
            "explanation": "CPUs provide privilege rings (Ring 0 for Kernel mode and Ring 3 for User mode). Privileged instructions can only be executed in Kernel mode via system calls."
        }
    ],
    "networks": [
        {
            "question_text": "In the TCP 3-way handshake, what flags are transmitted during the connection establishment phase?",
            "options": ["SYN -> SYN-ACK -> ACK", "ACK -> SYN -> ACK", "FIN -> ACK -> FIN-ACK", "SYN -> ACK -> DATA"],
            "correct_answer": "SYN -> SYN-ACK -> ACK",
            "explanation": "Client sends SYN; server responds with SYN-ACK; client acknowledges with ACK to establish a full-duplex TCP stream."
        },
        {
            "question_text": "At which layer of the OSI model does the Internet Protocol (IP) operate?",
            "options": ["Network Layer (Layer 3)", "Transport Layer (Layer 4)", "Data Link Layer (Layer 2)", "Session Layer (Layer 5)"],
            "correct_answer": "Network Layer (Layer 3)",
            "explanation": "The Network layer (Layer 3) handles packet routing, logical addressing (IPv4/IPv6), and forwarding across subnet boundaries."
        },
        {
            "question_text": "What cryptographic protocol encrypts HTTP traffic to provide confidentiality and integrity over the web?",
            "options": ["TLS (Transport Layer Security)", "SSH (Secure Shell)", "IPsec", "PGP"],
            "correct_answer": "TLS (Transport Layer Security)",
            "explanation": "HTTPS runs over TLS, which negotiates symmetric encryption keys using asymmetric cryptography to secure client-server communication."
        },
        {
            "question_text": "Which transport layer protocol is connectionless and prioritizes low latency over guaranteed packet delivery?",
            "options": ["UDP (User Datagram Protocol)", "TCP (Transmission Control Protocol)", "SCTP", "BGP"],
            "correct_answer": "UDP (User Datagram Protocol)",
            "explanation": "UDP sends independent datagrams without establishing a handshake or verifying receipt, making it ideal for real-time media, DNS queries, and gaming."
        },
        {
            "question_text": "What is the primary role of the Domain Name System (DNS)?",
            "options": ["Translating human-readable domain names to IP addresses", "Allocating MAC addresses to physical network cards", "Encrypting passwords during authentication", "Managing packet routing tables across autonomous systems"],
            "correct_answer": "Translating human-readable domain names to IP addresses",
            "explanation": "DNS acts as the internet's phonebook, translating hierarchical hostnames (e.g., edupath.ai) into machine-routable IP addresses."
        }
    ],
    "python": [
        {
            "question_text": "How does Python's Global Interpreter Lock (GIL) affect multithreaded CPU-bound programs in CPython?",
            "options": ["It prevents multiple native threads from executing Python bytecode simultaneously", "It distributes CPU-bound tasks across multiple cores automatically", "It prevents deadlocks between concurrent processes", "It replaces the garbage collection reference counter"],
            "correct_answer": "It prevents multiple native threads from executing Python bytecode simultaneously",
            "explanation": "CPython's GIL is a mutex that protects internal Python objects, restricting bytecode execution to a single thread at any moment, limiting CPU-bound multithreading."
        },
        {
            "question_text": "What type of object is returned when a function containing the 'yield' keyword is invoked in Python?",
            "options": ["Generator Object", "Iterator Tuple", "List Comprehension", "Coroutine Object"],
            "correct_answer": "Generator Object",
            "explanation": "A function that includes 'yield' returns a generator iterator object that computes values lazily upon successive calls to next()."
        },
        {
            "question_text": "What is the primary behavioral difference between 'is' and '==' in Python?",
            "options": ["'is' checks memory identity; '==' checks value equality", "'is' checks value equality; '==' checks type equivalence", "'is' performs deep copy comparisons; '==' performs shallow comparisons", "Both operators are completely identical"],
            "correct_answer": "'is' checks memory identity; '==' checks value equality",
            "explanation": "The 'is' operator evaluates whether two variables reference the exact same memory object (id(a) == id(b)), while '==' invokes __eq__ to compare values."
        },
        {
            "question_text": "Which built-in Python data structure maintains elements in insertion order while providing O(1) average lookup time?",
            "options": ["dict (Dictionary)", "set (Set)", "list (List)", "heapq"],
            "correct_answer": "dict (Dictionary)",
            "explanation": "Since Python 3.7+, the standard dict implementation is guaranteed to maintain insertion order while providing O(1) expected key lookup complexity."
        },
        {
            "question_text": "In Python object-oriented programming, what does the @staticmethod decorator indicate?",
            "options": ["The method receives neither an implicit self nor cls reference", "The method receives the class object as its first argument", "The method cannot return any value", "The method is executed before module import"],
            "correct_answer": "The method receives neither an implicit self nor cls reference",
            "explanation": "A @staticmethod does not receive an implicit first argument (neither self nor cls); it behaves like a regular function bound inside the class namespace."
        }
    ]
}


class QuizGeneratorService:
    def _strip_prefix(self, text: str) -> str:
        """Strips option enumeration prefixes like 'A) ', 'Option A: ', '1. ', '(B) '."""
        clean = re.sub(r'^(?:[A-Da-d1-4][\.\)]\s*|Option\s+[A-Da-d1-4]:?\s*|\([A-Da-d1-4]\)\s*)', '', text.strip())
        return clean.strip()

    def _normalize_options_and_answer(
        self,
        raw_options: List[str],
        raw_answer: str,
        topic_name: str
    ) -> Tuple[List[str], str]:
        """
        Normalizes quiz options and ensures the answer key matches an option verbatim.
        Deduplicates options, strips distracting letter prefixes, maps letter-only answers,
        and synthesizes plausible distractors if options count is insufficient.
        """
        cleaned_options = []
        seen = set()
        for opt in raw_options:
            s = self._strip_prefix(str(opt))
            if s and s.lower() not in seen:
                seen.add(s.lower())
                cleaned_options.append(s)

        raw_ans_str = str(raw_answer).strip()
        ans_stripped = self._strip_prefix(raw_ans_str)

        letter_map = {"a": 0, "b": 1, "c": 2, "d": 3, "1": 0, "2": 1, "3": 2, "4": 3}
        ans_lower = raw_ans_str.lower()

        # Check if raw_answer is a letter reference ("A", "Option B", "1")
        letter_match = re.match(r'^(?:option\s+)?([a-d1-4])(?:\)|:|\.|$)', ans_lower)
        matched_idx = letter_map.get(letter_match.group(1)) if letter_match else None

        correct_choice = ""
        if matched_idx is not None and matched_idx < len(cleaned_options):
            correct_choice = cleaned_options[matched_idx]
        elif ans_stripped.lower() in seen:
            for opt in cleaned_options:
                if opt.lower() == ans_stripped.lower():
                    correct_choice = opt
                    break
        else:
            # Substring match attempt
            for opt in cleaned_options:
                if ans_stripped.lower() in opt.lower() or opt.lower() in ans_stripped.lower():
                    correct_choice = opt
                    break

        # If answer could not be resolved, default to the first valid option or synthesize
        if not correct_choice and cleaned_options:
            correct_choice = cleaned_options[0]
        elif not correct_choice:
            correct_choice = f"{topic_name} guarantees structured operational invariants."
            cleaned_options.append(correct_choice)

        # Ensure at least 4 distinct options
        fallback_distractors = [
            f"It bypasses standard verification rules to maximize write throughput.",
            f"It executes exclusively in unprivileged user space without kernel validation.",
            f"It eliminates memory overhead by disabling rollback journals.",
            f"It provides unmonitored direct hardware access without virtualization."
        ]
        for dist in fallback_distractors:
            if len(cleaned_options) >= 4:
                break
            if dist.lower() not in seen:
                seen.add(dist.lower())
                cleaned_options.append(dist)

        # Final guarantee: correct_answer is in cleaned_options
        if correct_choice not in cleaned_options:
            cleaned_options[0] = correct_choice

        return cleaned_options[:4], correct_choice

    async def generate_quiz(
        self,
        topic_name: str,
        difficulty: str = "medium",
        question_count: int = 5,
        document_content: Optional[str] = None,
        subject_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes multiple-choice questions with difficulty-calibrated distractors,
        verifiable answer keys, and pedagogical explanations.
        """
        diff = difficulty.lower() if difficulty in ("easy", "medium", "hard") else "medium"
        count = max(1, min(question_count, 15))

        # 1. Attempt LLM synthesis
        subj_line = f"Subject: {subject_name}\n" if subject_name else ""
        doc_line = f"Reference Text:\n{document_content[:2000]}\n" if document_content else ""

        prompt = (
            f"Generate a {diff}-difficulty multiple choice assessment on '{topic_name}' "
            f"containing exactly {count} high-quality questions.\n"
            f"{subj_line}"
            f"{doc_line}\n"
            f"Return ONLY valid JSON as an array of objects with keys:\n"
            f"- question_text (string)\n"
            f"- options (list of 4 strings: distinct choices without letter prefixes)\n"
            f"- correct_answer (string matching one of the options verbatim)\n"
            f"- explanation (detailed pedagogical string explaining why the answer is correct)\n"
            f"- difficulty (string: easy, medium, or hard)"
        )

        llm_response = await llm_provider.generate_with_retry(
            prompt=prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 2048}
        )

        if llm_response:
            try:
                clean_json = re.sub(r"^```json\s*", "", llm_response.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE)
                parsed = json.loads(clean_json)
                if isinstance(parsed, list) and len(parsed) > 0:
                    validated = []
                    for item in parsed[:count]:
                        if "question_text" in item and "options" in item and "correct_answer" in item:
                            raw_opts = list(item["options"])
                            raw_ans = item["correct_answer"]
                            norm_opts, norm_ans = self._normalize_options_and_answer(raw_opts, raw_ans, topic_name)
                            validated.append({
                                "question_text": str(item["question_text"]).strip(),
                                "options": norm_opts,
                                "correct_answer": norm_ans,
                                "explanation": str(item.get("explanation", f"Correct answer for {topic_name}.")).strip(),
                                "difficulty": diff
                            })
                    if validated:
                        return validated
            except Exception as e:
                logger.warning(f"Failed to parse LLM quiz JSON: {e}")

        # 2. Deterministic Fallback Generation
        return self._generate_deterministic_quiz(topic_name, diff, count)

    def _generate_deterministic_quiz(self, topic: str, diff: str, count: int) -> List[Dict[str, Any]]:
        """
        Generates curriculum-grounded multiple-choice questions when LLM is offline.
        Uses specialized domain question banks when available, or dynamic topic-specific
        pedagogical generators.
        """
        t_lower = topic.lower()

        # Match domain question bank
        bank_key = None
        if any(k in t_lower for k in ("data structure", "algorithm", "dsa", "binary tree", "graph", "sorting")):
            bank_key = "dsa"
        elif any(k in t_lower for k in ("database", "dbms", "sql", "acid", "relation", "postgres")):
            bank_key = "dbms"
        elif any(k in t_lower for k in ("operating system", "os", "process", "deadlock", "memory management")):
            bank_key = "os"
        elif any(k in t_lower for k in ("network", "tcp", "ip", "dns", "http", "socket")):
            bank_key = "networks"
        elif any(k in t_lower for k in ("python", "fastapi", "django", "flask", "gil")):
            bank_key = "python"

        questions = []
        if bank_key and bank_key in CURRICULUM_QUESTION_BANKS:
            bank = CURRICULUM_QUESTION_BANKS[bank_key]
            for i in range(count):
                template = bank[i % len(bank)]
                norm_opts, norm_ans = self._normalize_options_and_answer(
                    template["options"], template["correct_answer"], topic
                )
                questions.append({
                    "question_text": template["question_text"],
                    "options": norm_opts,
                    "correct_answer": norm_ans,
                    "explanation": template["explanation"],
                    "difficulty": diff
                })
            return questions

        # Generic dynamic pedagogical question generator for arbitrary topics
        templates = [
            (
                f"What is the foundational principle or operational mechanism underlying {topic}?",
                f"{topic} enforces structured state transitions and mathematical correctness invariants.",
                [
                    f"{topic} bypasses relational integrity checks to maximize write throughput.",
                    f"{topic} executes exclusively in unprivileged user space without kernel validation.",
                    f"{topic} eliminates auxiliary memory overhead by disabling rollback journals."
                ],
                f"{topic} is architected to guarantee deterministic state transitions and maintain system correctness invariants."
            ),
            (
                f"Which key architectural trade-off is most commonly associated with {topic}?",
                f"Balancing latency, resource utilization, and consistency guarantees.",
                [
                    f"Completely eliminating the need for security sandboxing.",
                    f"Guaranteeing infinite throughput without additional compute hardware.",
                    f"Bypassing all network protocol handshakes unconditionally."
                ],
                f"In engineering systems involving {topic}, architects must continuously balance processing latency against resource limits and data consistency."
            ),
            (
                f"In practical software development, what is a primary best practice when implementing {topic}?",
                f"Employing modular boundaries, defensive error handling, and structured telemetry.",
                [
                    f"Hardcoding dynamic credentials directly in application source files.",
                    f"Disabling automated unit testing to accelerate release velocity.",
                    f"Supplying unchecked user input directly into system execution contexts."
                ],
                f"Best engineering practices require strong isolation, comprehensive validation, and robust logging around {topic}."
            ),
            (
                f"How does {topic} contribute to overall system scalability and maintainability?",
                f"By decoupling components and providing predictable interfaces for state management.",
                [
                    f"By tightly coupling database schemas with frontend presentation logic.",
                    f"By preventing concurrent requests from being queued or processed.",
                    f"By replacing asynchronous workflows with blocking synchronous calls."
                ],
                f"{topic} improves scalability by promoting loose coupling, clean contracts, and deterministic state handling."
            ),
            (
                f"What is the standard failure mode mitigation strategy applied to {topic}?",
                f"Graceful degradation with circuit breakers, fallbacks, and retry budgets.",
                [
                    f"Terminating the host operating system immediately upon first packet loss.",
                    f"Silently ignoring all runtime errors without logging or metric increments.",
                    f"Retrying failed requests in an infinite unthrottled loop."
                ],
                f"Reliable production systems implement circuit breaking, exponential backoff with jitter, and observability around {topic}."
            )
        ]

        for i in range(count):
            tpl = templates[i % len(templates)]
            q_text = tpl[0]
            correct = tpl[1]
            distractors = tpl[2]
            expl = tpl[3]

            options = [correct] + distractors
            rotated = options[i % 4:] + options[:i % 4]
            norm_opts, norm_ans = self._normalize_options_and_answer(rotated, correct, topic)

            questions.append({
                "question_text": q_text,
                "options": norm_opts,
                "correct_answer": norm_ans,
                "explanation": expl,
                "difficulty": diff
            })

        return questions

quiz_generator = QuizGeneratorService()
