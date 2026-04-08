# Phase 2: Utility and Application Analysis

Below are the answers regarding the impact, utility, and strategic alignment of the **File Sorter Enterprise** software for a company. (Context: A company focused on administration, finance, and media that processes large volumes of documents and digital files).

## Criterion 6a) Strategic Objectives
**What specific strategic objectives of the company does your software address?**
It directly addresses the reduction of operational downtime, mitigation of data loss risks regarding confidential information, and the establishment of standardized data governance.

**How does the software align with the overall digitalization strategy?**
It aligns by automating a mechanical task (file sorting) via intelligent desktop agents connected to a centralized backend infrastructure. This allows employees to focus on high-value tasks instead of losing hours organizing their local or shared file systems.

## Criterion 6b) Business and Communications Areas
**What areas of the company (production, business, communications) benefit the most from your software?**
The **Business/Finance** area benefits substantially (by automatically processing and routing invoices, budgets, or reports to the correct folders) alongside the **Communications/Marketing** area (by cleanly classifying multimedia materials, assets, and advertising documents into easily accessible directories).

**What operational impact do you expect in daily operations?**
I expect a drastic reduction of "digital clutter". Teams will no longer search for files in generic download folders; the local agent will automatically move items based on their extensions and content, achieving much faster and cleaner workflows.

## Criterion 6c) Areas Susceptible to Digitalization
**What areas of the company are most susceptible to being digitalized with your software?**
Overall document archive management; precisely, the entire circuit a file follows from the moment it is downloaded or generated until it is properly archived in the corporate intranet (legal, administrative, and accounting sectors).

**How will digitalization improve operations in those areas?**
By utilizing *File Sorter Enterprise*, operations shift from being manual and error-prone (e.g., misplacing a confidential file in a public folder) to programmatic, auditable operations fully documented in a unified database.

## Criterion 6d) Fit of Digitalized Areas (AD)
**How do digitalized areas interact with non-digitalized ones?**
Digitalized areas (e.g., the financial department using the File Sorter) automatically generate clean folder structures and reports (via automated system emails). Non-digitalized areas, or external stakeholders (such as auditors), can access these organized folders and read the emails without needing to directly interact with the underlying technology.

**What solutions or improvements would you propose to integrate these areas?**
To achieve maximum operative cohesion, I propose expanding the **automated email reporting** functionality so that anytime a financial invoice is detected and sorted, a specific payload is triggered to the Marketing/Communications team. This directly bridges the gap between the area executing the digitalization (Finance) and the area relying on non-digitalized input reviews (Communications), completely avoiding bottlenecks.

## Criterion 6e) Present and Future Needs
**What current needs of the company does your software solve?**
It efficiently resolves the pressing need to govern and secure daily digital information. It solves folder clutter, saturation of local transit drives (like "Downloads"), and protects access through modern JWT authentication.

For future needs, the decoupled design (Agent-Server) and the use of Docker allow the solution to scale seamlessly, effectively clearing the path for incorporating Artificial Intelligence to read PDF content before sorting it.

## Criterion 6f) Relationship with Technologies
**What enabling technologies have you used and how do they impact the company's areas?**
I have employed *FastAPI* for an asynchronous server backend, *CustomTkinter* for the employee interface, *WebSockets* for real-time file movement telemetry, and *Docker* for scaling *PostgreSQL*. This delivers a professional enterprise-grade ecosystem that communicates IT managers directly with employee workstations in real time.

**What specific benefits does the implementation of these technologies bring?**
Total flexibility (via REST APIs), real-time observability (via WebSockets), and secure dependency isolation preventing crashes in production databases (Docker).

## Criterion 6g) Security Breaches
**What possible security breaches could arise when implementing your software?**
Possible breaches include Man-In-The-Middle (MITM) attacks during rule synchronization between the agent and the server, or unauthorized access from an employee to physical database paths if local passwords are weak.

**What concrete measures would you propose to mitigate them?**
Already implemented in the project: The use of JWT-based authentication, database encryption using *BcRypt* / *Passlib*, and strict fault tolerance controls. For production environments, enforcing HTTPS and WSS (Secure WebSockets) through network infrastructure is strictly recommended.

## Criterion 6h) Data Management and Analysis
**How is data managed in your software and what methodologies do you use?**
User metadata and detailed *logs* of every moved file (name, origin, destination, hash signatures) are asynchronously pushed to a *PostgreSQL* backend validated under object-oriented *SQLModel* mechanisms.

**What do you do to guarantee the quality and consistency of the analyzed data?**
I use proactive validations through Pydantic integrated into FastAPI, preventing any defective *payload* and ensuring the database never processes corrupt telemetry. Also, Postgres ACID lock mechanisms are applied to prevent race conditions when multiple concurrent client rules clash simultaneously.

## Criterion 6i) Integration of Data, Applications, and Platforms
**How do systems interact and how does the software improve interoperability?**
The system integrates databases (Postgres), desktop applications (Tkinter Agent), and cloud-hosted platforms (FastAPI) utilizing a combination of REST APIs and bidirectional WebSockets. To improve interoperability, the platform automatically exposes an OpenAPI specification (Swagger) at `/docs`, allowing external CRM and ERP integrations.

## Criterion 6j) Documentation and Strategy
**Have you documented the changes made based on the strategy?**
Absolutely. A technical overview and changelog has been documented under the `wiki/devlog.md` inside this Open Source ecosystem. The devlog directly maps technical decisions (such as Backend isolation via Docker) to business resilience objectives.

## Criterion 6k) Human Resources Suitability
**What key skills are required and how is training planned?**
Staff trained in specific technical skills are necessary: **Python Asynchronous programming (FastAPI)**, **Relational Database Management (PostgreSQL/SQLModel)**, and **Event-Driven Architectures (WebSockets)**. 

To guarantee future viability and continuous training of new developers (onboarding), the entire codebase employs Sphinx/Google standard docstrings. Furthermore, the CI/CD pipeline generated a completely offline HTML Documentation Portal (`pdoc`), serving as an interactive training sandbox where junior developers can study the system's interoperability before making code changes.
