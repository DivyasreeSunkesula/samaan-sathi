# Samaan Sathi AI

AI-Powered Retail Management System for Small Shop Owners

## Quick Start

### Test Frontend Now (Backend Already Deployed)

```powershell
cd samaan-sathi
.\start.ps1
```

Opens http://localhost:8000 - Register and start using!

### Fix "User Not Confirmed" Error

```powershell
cd samaan-sathi
.\deploy.ps1
# Choose option 3
# Enter your username
```

### Full Deployment Menu

```powershell
cd samaan-sathi
.\deploy.ps1
```

Options:
1. Deploy Backend
2. Fix Login Issue
3. Confirm User
4. Test Locally
5. Deploy to S3
6. Get API URL

## Usage

1. Open http://localhost:8000
2. Click "Register"
3. Fill in your details:
   - Username: Choose a unique username
   - Password: Min 8 characters with uppercase, lowercase, and numbers
   - Email: Your email address
   - Phone: Format: +91XXXXXXXXXX
   - Full Name: Your full name
   - Shop Name: Your shop's name
4. Click "Register"
5. Login with your credentials
6. Start using the application!

## Features

- Dashboard with real-time stats
- Inventory management
- Udhaar (credit) tracking
- AI demand forecasting
- Pricing recommendations
- OCR bill scanner

## Troubleshooting

**Can't login after registration:**
```powershell
.\deploy.ps1
# Option 3 → Enter username
```

**Backend not found:**
```powershell
.\deploy.ps1
# Option 1 → Deploy Backend
```

## Documentation

- **API Reference:** [docs/API.md](docs/API.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Quick Reference:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

**Quick Start:** `.\start.ps1` - That's it!
