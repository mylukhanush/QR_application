# QR Code Multi-User Architecture Explained

## Problem Statement

**Challenge:** Multiple users need to scan the SAME QR code, but each user provides different information.

**Traditional Wrong Approach:**
```
Create unique QR for each user → MEM-001, MEM-002, MEM-003, etc.
Problem: Need new QR for every member
```

**Our Solution:**
```
One permanent QR code for all users → Points to Flask endpoint
Each user enters their own data → Validated against database
```

---

## Architecture Flow

### 1. QR Code Generation (One-time)

```python
# routes_registration.py or utils.py
def generate_registration_qr(app_url):
    registration_url = f'{app_url}/register'
    # This URL is encoded in the QR code, not user data
    img = QRCodeGenerator.generate_qr_code(registration_url)
    return img  # Same QR for all users
```

**Key Point:** QR code contains **URL only**, NOT user-specific data

### 2. Multi-User Access

```
User A                 User B                  User C
    ↓                     ↓                        ↓
[Scan QR]           [Scan QR]              [Scan QR]
    ↓                     ↓                        ↓
    └─────────────────┬────────────────────────┘
                      ↓
            http://localhost:5000/register
                      ↓
            └─→ Same endpoint for all!
                      ↓
        [Registration Form Opens]
                      ↓
    ┌───────────────┬──────────────┬───────────────┐
    ↓               ↓              ↓               ↓
  User A          User B        User C         User D
  fills            fills         fills           fills
  form             form          form            form
    ↓               ↓              ↓               ↓
  POST             POST           POST            POST
    ↓               ↓              ↓               ↓
Database          Database      Database        Database
records           records        records         records
separately        separately     separately      separately
```

### 3. Database Validation

```python
@registration_bp.route('/', methods=['POST'])
def register():
    mobile_number = request.form.get('mobile_number')
    
    # CRITICAL: Database-level uniqueness check
    existing_user = User.query.filter_by(
        mobile_number=mobile_number
    ).first()
    
    if existing_user:
        return "This mobile is already registered"
    
    # Create new user with auto-generated membership ID
    new_user = User(
        name=request.form.get('name'),
        age=request.form.get('age'),
        mobile_number=mobile_number,
        membership_id=generate_membership_id()  # MEM-XXXXX
    )
    db.session.add(new_user)
    db.session.commit()
    
    return "Registration successful"
```

---

## Why This Design is Secure

### 1. No Data in QR Code
```
❌ Bad: QR → {user_id: 5, name: "John", mobile: "9876543210"}
✅ Good: QR → http://localhost:5000/register
```

**Why it matters:**
- Can't decode QR to steal user data
- QR doesn't identify specific user
- Each scan shows form, not data

### 2. Backend Validation
```python
# Entry verification - STRICT validation
@entry_bp.route('/', methods=['POST'])
def verify_entry():
    user_input = request.form.get('mobile_number')
    
    # CRITICAL: Must exist in database
    user = User.query.filter_by(
        mobile_number=user_input
    ).first()
    
    if not user:
        # NO UNREGISTERED USER ALLOWED
        return "User Not Found - Must register first"
    
    # Check daily limit
    today_entry = EntryLog.query.filter(
        EntryLog.user_id == user.id,
        EntryLog.entry_date == date.today()
    ).first()
    
    if today_entry:
        return "Already checked in today"
    
    # All validations passed - create entry
    entry = EntryLog(user_id=user.id, entry_date=date.today())
    db.session.add(entry)
    db.session.commit()
```

### 3. Database Constraints
```sql
-- UNIQUE prevents duplicate registrations
ALTER TABLE users ADD UNIQUE(mobile_number);

-- FOREIGN KEY ensures entry points to valid user
ALTER TABLE entry_logs ADD FOREIGN KEY(user_id) 
    REFERENCES users(id) ON DELETE CASCADE;

-- COMPOSITE INDEX for efficient daily check
CREATE INDEX idx_user_date ON entry_logs(user_id, entry_date);
```

---

## Comparison: Single-Use vs Multi-Use QR

### Single-Use QR (DON'T DO THIS)

```
Problem 1: Need 1000 QR codes for 1000 members
Problem 2: Printing/storage nightmare
Problem 3: No scalability
Problem 4: QR lookup overhead

QR-001 → Member A
QR-002 → Member B
QR-003 → Member C
...
QR-1000 → Member Z

Code would be:
@app.route('/entry/<qr_code>')
def check_in(qr_code):
    entry = QRMapping.query.filter_by(qr_code=qr_code).first()
    if not entry:
        return "Invalid QR"
    return redirect to form
```

### Multi-Use QR (OUR APPROACH)

```
Benefit 1: ONE QR for infinite users
Benefit 2: Print once, use forever
Benefit 3: Fully scalable
Benefit 4: Simple endpoint

One permanent QR code → ALL members can scan
                    ↓
        Form validation in code
                    ↓
        Database checks user exists

@app.route('/register')  # Same for all users
def register():
    # Form shows
    # User enters their data
    # Database validates and stores
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     GYM MEMBER LIFECYCLE                    │
└─────────────────────────────────────────────────────────────┘

DAY 1 - REGISTRATION
═════════════════════════════════════════════════════════════

User A: Not registered
    ↓
    Scans Registration QR code
    ↓
    Browser navigates to /register
    ↓
    Sees form: Name, Age, Mobile, etc.
    ↓
    Fills: Name=John, Age=30, Mobile=9876543210
    ↓
    Clicks Submit
    ↓
    Backend validates:
    ├─ Name is valid? ✓
    ├─ Age is valid? ✓
    ├─ Mobile not duplicate? ✓ (check database)
    └─ All pass? ✓
    ↓
    Creates User record:
    ├─ id: 1 (auto-increment)
    ├─ name: "John"
    ├─ age: 30
    ├─ mobile_number: "9876543210"
    ├─ membership_id: "MEM-48372" (auto-generated)
    └─ registration_date: 2026-01-29 10:30:00
    ↓
    Success! Membership ID: MEM-48372

User B: Not registered (5 mins later)
    ↓
    Scans SAME Registration QR code
    ↓
    Browser navigates to /register (SAME URL)
    ↓
    Sees same form (fresh page for User B)
    ↓
    Fills: Name=Sarah, Age=28, Mobile=9123456789
    ↓
    Backend validates - all different data, all pass
    ↓
    Creates User record:
    ├─ id: 2 (auto-increment)
    ├─ name: "Sarah"
    ├─ age: 28
    ├─ mobile_number: "9123456789"
    ├─ membership_id: "MEM-91234" (auto-generated, unique)
    └─ registration_date: 2026-01-29 10:35:00
    ↓
    Success! Membership ID: MEM-91234


DAY 2 - CHECK-IN
═════════════════════════════════════════════════════════════

John (Member A): Registered
    ↓
    Scans Entry QR code
    ↓
    Browser navigates to /entry
    ↓
    Sees form: Mobile Number OR Membership ID
    ↓
    Enters: Mobile=9876543210
    ↓
    Backend validates:
    ├─ Query database: SELECT * FROM users WHERE mobile=?
    ├─ User found? ✓ (John, MEM-48372)
    ├─ Check today's entry: 
    │  SELECT * FROM entry_logs WHERE user_id=1 AND entry_date=TODAY
    ├─ Already entered today? ✗ (first time today)
    └─ All checks pass? ✓
    ↓
    Creates EntryLog record:
    ├─ id: 1 (auto-increment)
    ├─ user_id: 1 (John)
    ├─ entry_date: 2026-01-30
    ├─ entry_time: 2026-01-30 07:15:00
    └─ created_at: 2026-01-30 07:15:00
    ↓
    Success! Entry logged

John (Member A): Later same day
    ↓
    Scans Entry QR code AGAIN
    ↓
    Browser navigates to /entry
    ↓
    Enters: Mobile=9876543210
    ↓
    Backend validates:
    ├─ User found? ✓
    ├─ Check today's entry:
    │  SELECT * FROM entry_logs WHERE user_id=1 AND entry_date=TODAY
    ├─ Already entered today? ✓ (found 1 record)
    └─ BLOCK! Return error
    ↓
    Error! Already checked in today

Hacker: Unregistered person
    ↓
    Scans Entry QR code
    ↓
    Enters: Mobile=9999999999 (not registered)
    ↓
    Backend validates:
    ├─ Query database: SELECT * FROM users WHERE mobile=?
    ├─ User found? ✗ (no such user)
    └─ BLOCK! Return error
    ↓
    Error! User not found - must register first
```

---

## Code Examples

### Example 1: Registration with Multi-User Support

```python
@registration_bp.route('/', methods=['POST'])
def register():
    """
    Handle registration from form submission.
    Each user fills out own form → own database record
    """
    name = request.form.get('name').strip()
    age = int(request.form.get('age'))
    mobile_number = request.form.get('mobile_number').strip()
    
    # Strict validation
    if len(name) < 2:
        flash("Name too short", "error")
        return redirect(url_for('registration.register'))
    
    if age < 10 or age > 120:
        flash("Invalid age", "error")
        return redirect(url_for('registration.register'))
    
    # CRITICAL: Check mobile not duplicate
    existing = User.query.filter_by(mobile_number=mobile_number).first()
    if existing:
        flash("Mobile already registered", "error")
        return redirect(url_for('registration.register'))
    
    # Generate unique membership ID
    membership_id = generate_membership_id()
    
    # Create and save
    new_user = User(
        name=name,
        age=age,
        mobile_number=mobile_number,
        membership_id=membership_id
    )
    db.session.add(new_user)
    db.session.commit()
    
    flash(f"Registered! Your ID: {membership_id}", "success")
    return redirect(url_for('registration.register'))
```

### Example 2: Entry with Strict Validation

```python
@entry_bp.route('/', methods=['POST'])
def verify_entry():
    """
    Check-in validation.
    CRITICAL: No entry without registration!
    """
    mobile = request.form.get('mobile_number', '').strip()
    membership = request.form.get('membership_id', '').strip()
    
    # Find user (either mobile or membership)
    user = None
    if mobile:
        user = User.query.filter_by(mobile_number=mobile).first()
    elif membership:
        user = User.query.filter_by(membership_id=membership).first()
    else:
        flash("Enter mobile or membership ID", "error")
        return redirect(url_for('entry.verify_entry'))
    
    # CRITICAL VALIDATION: User must exist
    if not user:
        flash("User not found - must register first", "error")
        return redirect(url_for('entry.verify_entry'))
    
    # Check daily limit
    today = date.today()
    already_entered = EntryLog.query.filter(
        EntryLog.user_id == user.id,
        EntryLog.entry_date == today
    ).first()
    
    if already_entered:
        flash("Already checked in today", "warning")
        return redirect(url_for('entry.verify_entry'))
    
    # All validations passed - create entry
    entry = EntryLog(
        user_id=user.id,
        entry_date=today,
        entry_time=datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()
    
    flash(f"Entry logged! Welcome {user.name}", "success")
    return redirect(url_for('entry.verify_entry'))
```

---

## Key Takeaways

✅ **One QR = Many Users** - URL doesn't change, users do  
✅ **Form-based Input** - Each user provides data  
✅ **Strict Backend Validation** - Database checks everything  
✅ **No Data in QR** - Security through obscurity  
✅ **Scalable Forever** - Add unlimited members  
✅ **Database Integrity** - UNIQUE and FOREIGN KEY constraints  
✅ **Simple & Maintainable** - Easy to understand and extend

---

**Created:** January 29, 2026  
**Status:** Production Ready
