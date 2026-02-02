# Quick Start Guide - Gym QR Application

## ⚡ 5-Minute Setup

### Prerequisites Checklist
- [ ] Python 3.8+ installed (`python --version`)
- [ ] MySQL server running
- [ ] MySQL user created with privileges

### Step 1: Setup MySQL (2 minutes)

Open MySQL command line:
```sql
-- Create database
CREATE DATABASE gym_qr_db;

-- Create user
CREATE USER 'gym_user'@'localhost' IDENTIFIED BY 'secure_pass123';

-- Grant privileges
GRANT ALL PRIVILEGES ON gym_qr_db.* TO 'gym_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
```

### Step 2: Configure Application (1 minute)

Edit `config.py` line 9:
```python
# Change this:
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/gym_qr_db'

# To your credentials:
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://gym_user:secure_pass123@localhost/gym_qr_db'
```

### Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database (1 minute)

```bash
python database_setup.py
```

Should see:
```
Database Setup - Gym QR Application
============================================================
✓ Created database tables:
  - users
  - entry_logs
✓ Database initialization complete!
```

### Step 5: Run Application (0 seconds)

```bash
python app.py
```

Should see:
```
 * Running on http://localhost:5000
 * Debug mode: on
```

## 🌐 Access Application

**Home Page:**
- http://localhost:5000

**Registration:**
- http://localhost:5000/register

**Check-in:**
- http://localhost:5000/entry

**Admin Dashboard:**
- http://localhost:5000/admin/login
- Username: `admin`
- Password: `admin@123`

---

## 🧪 Test Workflow (10 minutes)

### Test 1: Register User

1. Go to http://localhost:5000/register
2. Fill form:
   - Name: John Doe
   - Age: 30
   - Mobile: 9876543210
3. Click Register
4. See: "Registration successful! Your Membership ID: MEM-XXXXX"

### Test 2: Try Duplicate Mobile

1. Go to http://localhost:5000/register
2. Fill same mobile: 9876543210
3. Click Register
4. See: "Mobile number is already registered"

### Test 3: Check-in User

1. Go to http://localhost:5000/entry
2. Enter Mobile: 9876543210
3. Click Check In
4. See: "Entry Successful! Welcome John Doe"

### Test 4: Try Check-in Again Same Day

1. Go to http://localhost:5000/entry
2. Enter Mobile: 9876543210
3. Click Check In
4. See: "Already Checked In Today"

### Test 5: Admin Dashboard

1. Go to http://localhost:5000/admin/login
2. Username: admin
3. Password: admin@123
4. Click Login
5. See Dashboard with:
   - Total Members: 1
   - Entered Today: 1
   - Not Entered Today: 0

### Test 6: View Members

1. Dashboard → "All Members"
2. Should see John Doe with membership ID

### Test 7: View Entry Logs

1. Dashboard → "Entry Logs"
2. Should see today's entry with timestamp

---

## 📱 QR Code Testing

### Generate QR Codes

**Option 1: View from Application**
- Registration QR: http://localhost:5000/register/qr
- Entry QR: http://localhost:5000/entry/qr

**Option 2: Print QR Codes**
1. Navigate to QR page
2. Click "Print QR Code"
3. Save as PDF

### Scan QR Codes

Use any QR code scanner app on phone:
1. Scan QR code
2. Click link that appears
3. Form loads in browser
4. Submit form

---

## 🔧 Configuration Reference

### Change Admin Credentials

Edit `config.py`:
```python
ADMIN_USERNAME = 'your_username'
ADMIN_PASSWORD = 'your_secure_password'
```

### Change Database

Edit `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@host/dbname'
```

### Change Items Per Page

Edit `config.py`:
```python
ITEMS_PER_PAGE = 50  # Default is 20
```

### Change Application Port

Edit `app.py` last line:
```python
app.run(host='localhost', port=8080, debug=True)
```

---

## 🐛 Common Issues & Solutions

### Issue: "Can't connect to MySQL"
```
Error: (pymysql.err.OperationalError) (2003, "Can't connect...")
```
**Solution:**
1. Ensure MySQL is running: `mysql -u root -p`
2. Check credentials in config.py
3. Verify database exists: `SHOW DATABASES;`

### Issue: "Table already exists"
```
Error: sqlalchemy.exc.IntegrityError: Table 'users' already exists
```
**Solution:**
1. Delete existing tables: `DROP TABLE entry_logs; DROP TABLE users;`
2. Run: `python database_setup.py`

### Issue: "ModuleNotFoundError: No module named 'flask'"
```
Error: ImportError
```
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No such file or directory: templates/registration.html"
```
Error: FileNotFoundError
```
**Solution:**
1. Ensure templates folder exists: `ls templates/`
2. Ensure all template files are in `templates/` folder

---

## 📊 Folder Structure Check

After setup, your folder should look like:
```
QR Application/
├── app.py ✓
├── config.py ✓
├── models.py ✓
├── utils.py ✓
├── routes_registration.py ✓
├── routes_entry.py ✓
├── routes_admin.py ✓
├── database_setup.py ✓
├── requirements.txt ✓
├── README.md ✓
├── QR_ARCHITECTURE.md ✓
├── QUICKSTART.md ✓
├── static/
│   └── style.css ✓
└── templates/
    ├── base.html ✓
    ├── index.html ✓
    ├── registration.html ✓
    ├── entry.html ✓
    ├── qr_display.html ✓
    ├── admin_login.html ✓
    ├── admin_dashboard.html ✓
    ├── admin_users.html ✓
    ├── admin_entries.html ✓
    ├── admin_not_entered.html ✓
    ├── admin_statistics.html ✓
    ├── 404.html ✓
    └── 500.html ✓
```

---

## 📈 Next Steps (Production)

Before deploying to production:

1. **Security**
   - [ ] Change admin password in config.py
   - [ ] Use environment variables for credentials
   - [ ] Enable HTTPS (set SESSION_COOKIE_SECURE = True)
   - [ ] Use strong database password

2. **Database**
   - [ ] Create database backup
   - [ ] Setup automated backups
   - [ ] Enable query logging

3. **Deployment**
   - [ ] Use production server (Gunicorn)
   - [ ] Setup reverse proxy (Nginx/Apache)
   - [ ] Enable SSL/TLS certificates
   - [ ] Configure logging

4. **Monitoring**
   - [ ] Setup error tracking (Sentry)
   - [ ] Add application logging
   - [ ] Monitor database performance

---

## 📞 Support

**For issues:**
1. Check README.md - Troubleshooting section
2. Check QR_ARCHITECTURE.md - Design explanation
3. Review code comments in source files
4. Check terminal output for error messages

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] http://localhost:5000 loads
- [ ] Registration form appears at /register
- [ ] Check-in form appears at /entry
- [ ] Admin login at /admin/login
- [ ] Admin dashboard shows stats
- [ ] Can register a member
- [ ] Duplicate mobile blocked
- [ ] Can check-in registered member
- [ ] Duplicate check-in blocked
- [ ] QR codes display at /register/qr and /entry/qr

---

**Estimated total setup time: 5-10 minutes**

**First successful registration: 2 minutes**

**Full application test: 10 minutes**

---

Created: January 29, 2026  
Version: 1.0 - Production Ready
