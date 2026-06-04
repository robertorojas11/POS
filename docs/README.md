# ApexPOS Documentation Center

Welcome to the **ApexPOS Documentation Center**. This directory contains user manuals, operational directives, and system architecture guides for the ApexPOS platform.

---

## 📖 Documentation Index

### 1. User & Operations Manuals
Step-by-step user guides for each user role in the system:
* **[Operator User Manual](file:///D:/ERP/POS/docs/user_manuals/operator_manual.md)**: Daily register operations, decimal UOM entries, offline checkouts, and shift turns.
* **[Manager User Manual](file:///D:/ERP/POS/docs/user_manuals/manager_manual.md)**: Live register monitoring, cash drops, inventory configuration, and sales auditing.
* **[Administrator User Manual](file:///D:/ERP/POS/docs/user_manuals/admin_manual.md)**: System configuration, employee role provisioning, and promotional coupon setup.

### 2. Architecture & Directives
Deep dives into system mechanisms, caching policies, and data synchronization:
* **[Offline-First & Data Sync Architecture](file:///D:/ERP/POS/docs/architecture/offline_sync.md)**: Technical detail on IndexedDB wrappers, offline queues, inventory safety deductions, and automatic background sync.
* **[Multi-Terminal Cache & SSE Sync](file:///D:/ERP/POS/docs/architecture/terminal_caching_sse.md)**: Server-Sent Events notification mechanism, terminal Redis key namespaces, and catalog invalidation rules.

---

## 🛠️ Codebase Structure Reference

For development guidelines and backend/frontend patterns, refer to:
* **[Agent Instructions Router (AGENTS.md)](file:///D:/ERP/POS/AGENTS.md)**
* **[Coding Standards & Rules (coding_standards.md)](file:///D:/ERP/POS/.agents/rules/coding_standards.md)**
* **[Installation and Setup (README.md)](file:///D:/ERP/POS/README.md)**
