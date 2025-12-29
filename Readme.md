# Ops System – Internal Operations & Task Management Platform

A role-based internal operations system designed for small to mid-sized businesses to manage **orders, tasks, inventory, and payments** with clear workflows and accountability.

This project is built as a **demo-ready MVP** showcasing clean architecture, real-world business logic, and operational dashboards.

---

## 🚀 Key Features

### 👥 Role-Based Access
- **Admin**
  - Create and manage orders
  - Monitor overall operations via dashboards
  - View metrics, charts, and system health
- **Staff**
  - View assigned tasks
  - Track workload and due dates
  - Update task progress

---

### 📦 Order Management
- Orders linked to products and quantities
- Automatic stock reservation on order creation
- Order lifecycle:
  - `NEW` → `IN_PROGRESS` → `COMPLETED`
  - Safe cancellation with stock rollback
- Orders automatically complete when all related tasks are finished

---

### ✅ Task Management
- Tasks linked to orders
- Tasks cannot be assigned to cancelled or completed orders
- Task workflow:
  - `PENDING` → `IN_PROGRESS` → `COMPLETED`
- Due dates and overdue tracking
- Auto-cleanup of tasks when an order is cancelled

---

### 📊 Dashboards & Metrics

#### Admin Dashboard
- Orders today
- Pending orders
- Pending tasks
- Charts:
  - Orders over last 7 days
  - Task status distribution

#### Staff Dashboard
- Pending tasks
- Tasks completed today
- Task status breakdown
- Pending vs overdue tasks
- Tasks due today widget

---

### 🧮 Inventory Management
- Centralized product stock tracking
- Race-condition safe stock updates
- Stock movements logged as immutable records
- Supports:
  - Order-based stock deduction
  - Restocking
  - Safe rollback on cancellations

---

### 💰 Payments & Refunds
- Payments linked to orders
- Immutable payment records
- Refunds handled as compensating transactions (no edits/deletes)
- Automatic refund on order cancellation (if payment exists)

---

### 🎨 UI & UX
- Clean sidebar-based layout
- Fixed navigation, scrollable content
- Tailwind CSS for styling
- Chart.js for data visualization
- Loading indicators
- Role-aware navigation
- Professional admin-style UI

---

## 🛠 Tech Stack

- **Backend**: Django (Python)
- **Frontend**: Django Templates + Tailwind CSS
- **Database**: SQLite (for demo; easily replaceable)
- **Charts**: Chart.js
- **Auth**: Django authentication system

---

## 🧱 Architecture Highlights

- Business logic inside models (not views)
- Transaction-safe operations (`transaction.atomic`)
- Separation of concerns:
  - `orders`
  - `tasks`
  - `inventory`
  - `payments`
  - `core`
- Scalable and production-friendly structure

---

## ▶️ Typical Workflow

1. Admin creates an order
2. Stock is reserved automatically
3. Tasks are assigned to staff
4. Staff completes tasks
5. Order auto-completes when all tasks finish
6. Admin monitors progress via dashboard
7. If cancelled:
   - Stock is returned
   - Tasks are removed
   - Refund is issued if applicable

---

## 🎯 Purpose of This Project

This project is intended to:
- Demonstrate real-world backend design
- Serve as a **demo MVP** for client discussions
- Act as a foundation for a potential **Micro-SaaS product**
- Showcase clean Django architecture and operational thinking

---

## 📌 Notes

- This is a demo-focused implementation
- Mobile optimization and advanced notifications are intentionally out of scope
- The system is designed to be extended easily

---

## 📄 License

This project is provided as a demonstration and learning reference.
