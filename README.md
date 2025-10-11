# InSight - Real-Time Analytics Dashboard

![InSight Dashboard Demo GIF](<img width="1919" height="972" alt="Image" src="https://github.com/user-attachments/assets/a8c1b918-fac3-47e0-979a-6855c72586d0" />)

## Description

InSight is a feature-complete, full-stack web application that provides real-time data visualization and analytics. It features a secure, token-based authentication system, a live data ingestion pipeline, and a dynamic, component-based frontend.

This project was built from the ground up as a comprehensive, hands-on learning experience to master the architecture and challenges of building modern, real-world web applications.

---
## Core Features

* **Secure Authentication:** Full user registration and login system using JWT for secure, token-based access.
* **Protected Routes:** Dashboard and data endpoints are fully protected and accessible only to authenticated users.
* **Real-Time Data Visualizations:** A historical line chart and a large numerical display update in real-time to reflect the latest data.
* **Robust Backend API:** A high-performance RESTful API built with Python and FastAPI, complete with interactive Swagger documentation.

---
## Tech Stack

* **Frontend:** React, TypeScript, Vite, React Router, Chart.js
* **Backend:** Python, FastAPI
* **Database:** PostgreSQL with the TimescaleDB extension
* **DevOps:** Docker & Docker Compose
* **Authentication:** JWT, Passlib (bcrypt hashing)

---
## 🚀 Project Journey & Key Learnings

This project was a mentor-guided deep dive into full-stack development. The primary focus was on understanding system architecture and solving the complex problems that arise when integrating multiple technologies.

Key challenges I successfully debugged and resolved include:
* Configuring the local development environment, including system PATH variables and PowerShell execution policies.
* Diagnosing and fixing a circular import dependency in the Python backend by refactoring the application structure.
* Implementing and troubleshooting CORS to enable secure communication between the frontend and backend.
* Managing a multi-service application with Docker and orchestrating three concurrent terminal processes for the database, backend, and frontend.

---
## Local Development

[We can add instructions here later on how another developer can run your project.]