# Architecture & System Diagrams

## 1️⃣ Application Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GYM QR APPLICATION                       │
│                   ARCHITECTURE DIAGRAM                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  USER (Browser)  │
└────────┬─────────┘
         │
         │ HTTP Request
         ▼
┌──────────────────────────────────────────────────────────────┐
│              FLASK APPLICATION (app.py)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Blueprint Architecture                        │ │
│  │                                                        │ │
│  │  ┌──────────────────┐  ┌──────────────────────────┐  │ │
│  │  │ Registration BP  │  │ Entry/Check-in BP      │  │ │
│  │  │  /register       │  │ /entry                 │  │ │
│  │  │  GET/POST        │  │ GET/POST               │  │ │
│  │  │                  │  │                        │  │ │
│  │  │ ┌──────────────┐ │  │ ┌──────────────────┐  │  │
│  │  │ │Form Display  │ │  │ │Form Display      │  │  │
│  │  │ │Form Submit   │ │  │ │User Lookup       │  │  │
│  │  │ │Validation    │ │  │ │Daily Limit Check │  │  │
│  │  │ │User Creation │ │  │ │Entry Creation    │  │  │
│  │  │ └──────────────┘ │  │ └──────────────────┘  │  │
│  │  └──────────────────┘  └──────────────────────────┘  │
│  │                                                        │
│  │  ┌──────────────────────────────────────────────┐    │
│  │  │ Admin Blueprint                              │    │
│  │  │ /admin                                       │    │
│  │  │ GET/POST                                    │    │
│  │  │                                             │    │
│  │  │ ├─ Login/Logout                             │    │
│  │  │ ├─ Dashboard (stats)                        │    │
│  │  │ ├─ View Users (search, pagination)          │    │
│  │  │ ├─ View Entries (date filter)              │    │
│  │  │ ├─ View Not Entered                         │    │
│  │  │ └─ Statistics (trends)                      │    │
│  │  └──────────────────────────────────────────────┘    │
│  └────────────────────────────────────────────────────────┘
│                          │
│                          │ Database Operations
│                          ▼
│        ┌─────────────────────────────────┐
│        │  SQLAlchemy ORM Models          │
│        │                                 │
│        │ ├─ User (Registration Data)    │
│        │ └─ EntryLog (Check-in Data)    │
│        └─────────────────────────────────┘
└──────────────────────────────────────────────────────────────┘
         │
         │ SQL Queries
         ▼
┌──────────────────────────────────────────────────────────────┐
│              MYSQL DATABASE                                  │
│                                                              │
│  ┌─────────────────────┐  ┌──────────────────────────────┐ │
│  │ users TABLE         │  │ entry_logs TABLE            │ │
│  │                     │  │                             │ │
│  │ id (PK)             │  │ id (PK)                     │ │
│  │ name                │  │ user_id (FK) ───────────┐  │ │
│  │ age                 │  │ entry_date              │  │ │
│  │ mobile_number (UQ)  │  │ entry_time              │  │ │
│  │ membership_id (UQ)  │  │ exit_time               │  │ │
│  │ registration_date   │  │ created_at              │  │ │
│  │ updated_at          │  │                         │  │ │
│  │                     │  │ INDEXES:                │  │ │
│  │ INDEXES:            │  │ - idx_entry_date        │  │ │
│  │ - idx_mobile        │  │ - idx_user_date (PK)    │  │ │
│  │ - idx_membership    │  │                         │  │ │
│  │                     │  │ CONSTRAINTS:            │  │ │
│  │ CONSTRAINTS:        │  │ - FK to users(id)       │  │ │
│  │ - UNIQUE mobile     │  │ - CASCADE delete        │  │ │
│  │ - UNIQUE membership │  └──────────────────────────────┘ │
│  └─────────────────────┘                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ Data Flow Diagram

### Registration Flow

```
┌─────────────────────────────────────────────────────────────┐
│              REGISTRATION DATA FLOW                         │
└─────────────────────────────────────────────────────────────┘

User                QR Code               Flask App           Database
 │                    │                      │                   │
 │ Scan QR Code       │                      │                   │
 │───────────────────→│                      │                   │
 │                    │                      │                   │
 │                    │ Navigate to /register│                   │
 │                    │─────────────────────→│                   │
 │                    │                      │                   │
 │   Registration Form Displayed             │                   │
 │←─────────────────────────────────────────│                   │
 │                    │                      │                   │
 │ Fill: Name, Age, Mobile                  │                   │
 │ Submit POST /register                    │                   │
 │──────────────────────────────────────────→│                   │
 │                    │                      │                   │
 │                    │  ┌──────────────┐    │                   │
 │                    │  │ VALIDATION   │    │                   │
 │                    │  ├──────────────┤    │                   │
 │                    │  │ Name valid?  │    │                   │
 │                    │  │ Age valid?   │    │                   │
 │                    │  │ Mobile fmt?  │    │                   │
 │                    │  └──────────────┘    │                   │
 │                    │       ↓              │                   │
 │                    │  ┌──────────────┐    │                   │
 │                    │  │ DB LOOKUP    │    │                   │
 │                    │  └──────────────┘    │                   │
 │                    │       │              │                   │
 │                    │       └─────────────→│ SELECT * FROM users
 │                    │                      │ WHERE mobile_number=?
 │                    │                      │                   │
 │                    │                      │←────────────────────
 │                    │                      │ Result: Not found ✓
 │                    │                      │                   │
 │                    │  ┌──────────────┐    │                   │
 │                    │  │ GENERATE ID  │    │                   │
 │                    │  │ MEM-XXXXX    │    │                   │
 │                    │  └──────────────┘    │                   │
 │                    │                      │                   │
 │                    │  ┌──────────────┐    │                   │
 │                    │  │ CREATE USER  │    │                   │
 │                    │  └──────────────┘    │                   │
 │                    │                      │                   │
 │                    │                      │─────────────────→│
 │                    │                      │ INSERT INTO users
 │                    │                      │ VALUES (...)
 │                    │                      │                   │
 │                    │                      │←────────────────────
 │                    │                      │ Success: ID=1
 │                    │                      │                   │
 │ Success Message    │                      │                   │
 │ "Membership: MEM-48372"                  │                   │
 │←──────────────────────────────────────────│                   │
 │                    │                      │                   │
```

### Entry Flow

```
┌─────────────────────────────────────────────────────────────┐
│              ENTRY/CHECK-IN DATA FLOW                       │
└─────────────────────────────────────────────────────────────┘

User                QR Code               Flask App           Database
 │                    │                      │                   │
 │ Scan Entry QR      │                      │                   │
 │───────────────────→│                      │                   │
 │                    │                      │                   │
 │                    │ Navigate to /entry   │                   │
 │                    │─────────────────────→│                   │
 │                    │                      │                   │
 │   Entry Form       │                      │                   │
 │←─────────────────────────────────────────│                   │
 │                    │                      │                   │
 │ Enter Mobile/ID    │                      │                   │
 │ Submit             │                      │                   │
 │──────────────────────────────────────────→│                   │
 │                    │                      │                   │
 │                    │  ┌──────────────────┐ │                   │
 │                    │  │ VALIDATION       │ │                   │
 │                    │  │ Input required?  │ │                   │
 │                    │  └──────────────────┘ │                   │
 │                    │       ↓               │                   │
 │                    │  ┌──────────────────┐ │                   │
 │                    │  │ FIND USER        │ │                   │
 │                    │  └──────────────────┘ │                   │
 │                    │       │               │                   │
 │                    │       └──────────────→│ SELECT * FROM users
 │                    │                       │ WHERE mobile_number=?
 │                    │                       │                   │
 │                    │                       │←────────────────────
 │                    │                       │ Result: Found (John)
 │                    │       ┌─ User found? YES
 │                    │       │
 │                    │       └─ Proceed to daily check
 │                    │
 │                    │  ┌──────────────────────────┐
 │                    │  │ CHECK DAILY LIMIT        │
 │                    │  │ Composite index query    │
 │                    │  └──────────────────────────┘
 │                    │       │                      │
 │                    │       └─────────────────────→│ SELECT * FROM entry_logs
 │                    │                              │ WHERE user_id=1
 │                    │                              │ AND entry_date=TODAY
 │                    │                              │
 │                    │                              │←─────────────────
 │                    │                              │ Result: 0 rows
 │                    │  ┌──────────────────┐       │
 │                    │  │ CREATE ENTRY     │       │
 │                    │  └──────────────────┘       │
 │                    │       │                      │
 │                    │       └─────────────────────→│ INSERT INTO entry_logs
 │                    │                              │ VALUES (user_id=1, ...)
 │                    │                              │
 │                    │                              │←─────────────────
 │                    │                              │ Success
 │                    │                              │
 │ Entry Logged       │                              │
 │ "Welcome John"     │                              │
 │←─────────────────────────────────────────────────│
 │                    │                              │
```

---

## 3️⃣ System Components Interaction

```
┌────────────────────────────────────────────────────────────────┐
│                COMPONENT INTERACTION DIAGRAM                  │
└────────────────────────────────────────────────────────────────┘

                        ┌──────────────────┐
                        │  config.py       │
                        │  Settings        │
                        │  Credentials     │
                        └────────┬─────────┘
                                 │
                   ┌─────────────┼──────────────┐
                   │             │              │
                   ▼             ▼              ▼
            ┌─────────────┐ ┌──────────┐ ┌──────────────┐
            │  app.py     │ │models.py │ │utils.py      │
            │ Main App    │ │Database  │ │QR Generation │
            │ & Routes    │ │Models    │ │              │
            └─────────────┘ └──────────┘ └──────────────┘
                   │             │              │
                   └─────────────┼──────────────┘
                                 │
                   ┌─────────────┴──────────────┐
                   │                            │
                   ▼                            ▼
            ┌─────────────────────┐  ┌─────────────────┐
            │ BLUEPRINTS          │  │ TEMPLATES       │
            │                     │  │                 │
            │ routes_registration │  │ registration.html
            │ routes_entry        │  │ entry.html
            │ routes_admin        │  │ admin_*.html
            │                     │  │                 │
            └──────────┬──────────┘  └────────┬────────┘
                       │                      │
                       └──────────┬───────────┘
                                  │
                         ┌────────▼──────────┐
                         │                   │
                         │  STATIC FILES     │
                         │  style.css        │
                         │                   │
                         └────────┬──────────┘
                                  │
                         ┌────────▼──────────┐
                         │                   │
                         │  MYSQL DATABASE   │
                         │  users            │
                         │  entry_logs       │
                         │                   │
                         └───────────────────┘
```

---

## 4️⃣ Request Response Cycle

```
┌────────────────────────────────────────────────────────────────┐
│            HTTP REQUEST/RESPONSE CYCLE                        │
└────────────────────────────────────────────────────────────────┘

CLIENT                          FLASK                         DATABASE
(Browser)                    (Backend)

   │
   │ GET /register
   ├────────────────────────→
   │                          │
   │                          ├─ Route: registration.register()
   │                          │
   │                          ├─ render_template('registration.html')
   │
   ←──────────────────────────
   │ HTML Form
   │

   │
   │ POST /register
   │ {name, age, mobile}
   ├────────────────────────→
   │                          │
   │                          ├─ Validate inputs
   │                          │
   │                          ├─ Check database for duplicate
   │                          ├───────────────────────────→
   │                          │                          │
   │                          │←─────────────────────────
   │                          │ SELECT result
   │                          │
   │                          ├─ Generate membership ID
   │                          │
   │                          ├─ Create user object
   │                          │
   │                          ├─ db.session.add(user)
   │                          ├─ db.session.commit()
   │                          ├───────────────────────────→
   │                          │                          │
   │                          │←─────────────────────────
   │                          │ INSERT success
   │                          │
   │                          ├─ Flash message
   │                          ├─ Redirect
   │
   ←──────────────────────────
   │ Success Page
   │
```

---

## 5️⃣ Database Relationships

```
┌────────────────────────────────────────────────────────────────┐
│               ENTITY RELATIONSHIP DIAGRAM (ERD)               │
└────────────────────────────────────────────────────────────────┘

        ┌────────────────────────────────────────┐
        │          USERS (Members)               │
        ├────────────────────────────────────────┤
        │ id (PK)                                │
        │ name                                   │
        │ age                                    │
        │ mobile_number (UNIQUE) ←────────┐     │
        │ membership_id (UNIQUE)          │     │
        │ registration_date               │     │
        │ updated_at                      │     │
        └────────────────────────────────┬──────┘
                                         │
                                         │ 1
                                         │
                                         │
                                    Has Many
                                         │
                                         │ N
                                         │
        ┌────────────────────────────────▼──────┐
        │      ENTRY_LOGS (Check-ins)           │
        ├──────────────────────────────────────┤
        │ id (PK)                               │
        │ user_id (FK) ──────────┘              │
        │ entry_date                            │
        │ entry_time                            │
        │ exit_time                             │
        │ created_at                            │
        └──────────────────────────────────────┘

Cardinality: 1 User : Many Entries
Constraint: FOREIGN KEY (user_id) REFERENCES users(id)
Delete Rule: ON DELETE CASCADE
Index: (user_id, entry_date)
```

---

## 6️⃣ Security Validation Flow

```
┌────────────────────────────────────────────────────────────────┐
│         SECURITY & VALIDATION FLOW DIAGRAM                    │
└────────────────────────────────────────────────────────────────┘

INPUT
  │
  ├─ User submits form
  │
  ▼
FORM VALIDATION (Python)
  │
  ├─ Check name length
  ├─ Check age range
  ├─ Check mobile format
  │
  ├─ If invalid → REJECT
  │              Error message
  │              Show form again
  │
  ▼
DATABASE VALIDATION (SQLAlchemy + MySQL)
  │
  ├─ Check UNIQUE mobile_number
  │
  ├─ If duplicate → REJECT
  │               Error message
  │
  ├─ Check FOREIGN KEY user_id (for entries)
  │
  ├─ If invalid user → REJECT
  │                  Error message
  │
  ├─ Check UNIQUE membership_id
  │
  ├─ If duplicate → REJECT
  │               Error message (shouldn't happen)
  │
  ▼
BUSINESS LOGIC VALIDATION
  │
  ├─ Check daily entry limit
  │ SELECT * FROM entry_logs WHERE user_id=? AND entry_date=TODAY
  │
  ├─ If exists → REJECT
  │           Error: "Already checked in"
  │
  ▼
COMMIT TO DATABASE
  │
  ├─ INSERT/UPDATE executed
  ├─ Transaction committed
  ├─ Success confirmed
  │
  ▼
RESPONSE TO USER
  │
  ├─ Flash success message
  ├─ Redirect to success page
  │
  ▼
LOGGED & STORED
  │
  ├─ Data in database
  ├─ Admin can view
  ├─ Reports available
  │
```

---

## 7️⃣ Admin Dashboard Data Flow

```
┌────────────────────────────────────────────────────────────────┐
│          ADMIN DASHBOARD DATA AGGREGATION FLOW                │
└────────────────────────────────────────────────────────────────┘

Admin Access
    │
    ├─ Login page
    │    │
    │    ├─ Validate credentials
    │    ├─ Create session
    │    │
    │    ▼
    ├─ Redirect to dashboard
    │    │
    │    ├─ Query 1: Total users
    │    │   SELECT COUNT(*) FROM users
    │    │
    │    ├─ Query 2: Entered today
    │    │   SELECT COUNT(DISTINCT user_id) FROM entry_logs
    │    │   WHERE entry_date = TODAY
    │    │
    │    ├─ Query 3: Not entered today
    │    │   Total - Entered = Not Entered
    │    │
    │    ├─ Query 4: Recent registrations
    │    │   SELECT * FROM users ORDER BY registration_date DESC LIMIT 5
    │    │
    │    ├─ Query 5: Today's entries
    │    │   SELECT * FROM entry_logs JOIN users...
    │    │   WHERE entry_date = TODAY
    │    │
    │    ▼
    ├─ Render dashboard with statistics
    │
    ├─ View all members
    │    │
    │    ├─ Optional search
    │    ├─ Pagination
    │    │
    │    ▼
    ├─ View entry logs
    │    │
    │    ├─ Date filter
    │    ├─ Pagination
    │    │
    │    ▼
    ├─ View not entered users
    │    │
    │    ├─ Subquery for comparison
    │    │
    │    ▼
    ├─ View statistics
    │    │
    │    ├─ 7-day trends
    │    ├─ Registration trends
    │    │
    │    ▼
    └─ Logout
         │
         ├─ Clear session
         ├─ Redirect to home
         │
```

---

## 8️⃣ Multi-User QR Security Model

```
┌────────────────────────────────────────────────────────────────┐
│         MULTI-USER QR CODE SECURITY MODEL                     │
└────────────────────────────────────────────────────────────────┘

TRADITIONAL APPROACH (INSECURE):
┌──────────────────────────────────────────────────────────┐
│ QR Code 1 → Token "ABC123" → User 1                     │
│ QR Code 2 → Token "DEF456" → User 2                     │
│ QR Code 3 → Token "GHI789" → User 3                     │
│                                                          │
│ Problems:                                                │
│ - Need 1000 QR codes for 1000 users                    │
│ - Tokens visible in URLs/QR                            │
│ - Tokens can be reused, shared                         │
│ - Database lookup complex                              │
└──────────────────────────────────────────────────────────┘

OUR APPROACH (SECURE):
┌──────────────────────────────────────────────────────────┐
│                                                          │
│ ONE PERMANENT QR CODE                                   │
│      ↓                                                   │
│ Points to: /register or /entry URL                      │
│      ↓                                                   │
│ User fills form with their data                         │
│      ├─ Mobile number                                   │
│      └─ Membership ID                                   │
│      ↓                                                   │
│ BACKEND VALIDATES:                                      │
│      ├─ Query: SELECT * FROM users WHERE mobile=?     │
│      ├─ Query: SELECT * FROM entry_logs WHERE ...      │
│      └─ Apply business rules                           │
│      ↓                                                   │
│ DATABASE ENFORCES:                                      │
│      ├─ UNIQUE constraint on mobile                    │
│      ├─ FOREIGN KEY constraint on user_id             │
│      └─ Composite index on (user_id, date)            │
│      ↓                                                   │
│ RESULT: Secure, scalable, efficient                    │
│                                                          │
│ Benefits:                                                │
│ ✓ One QR = infinite users                              │
│ ✓ No tokens in URL                                     │
│ ✓ No token sharing possible                            │
│ ✓ Database validates everything                        │
│ ✓ Full audit trail                                     │
│ ✓ Scalable forever                                     │
└──────────────────────────────────────────────────────────┘
```

---

## Summary

These diagrams show how the system:
1. Routes requests through Flask blueprints
2. Validates data at multiple levels
3. Enforces security at database level
4. Provides secure multi-user QR support
5. Maintains data integrity
6. Enables efficient admin dashboard

**Key Point:** Multiple layers of validation + database constraints = secure, reliable system
