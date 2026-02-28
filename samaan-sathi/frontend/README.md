# Samaan Sathi AI - Frontend

Complete web application for Samaan Sathi AI retail companion system.

## Features

### 🏠 Dashboard
- Real-time statistics (Total Items, Low Stock, Udhaar, Alerts)
- Recent alerts display
- AI-powered recommendations
- Quick overview of shop performance

### 📦 Inventory Management
- View all inventory items
- Add new items with cost/selling price
- Filter by category
- Search functionality
- Low stock indicators
- Margin calculations

### 💰 Udhaar (Credit) Management
- Track customer credit
- View outstanding amounts
- Record payments
- Filter by status (Pending/Overdue/Paid)
- Customer-wise ledger
- Risk indicators

### 📊 Demand Forecast
- 7-day demand predictions
- Visual forecast charts
- AI-powered recommendations
- Confidence scores
- Optimal stock suggestions

### 💵 Pricing Recommendations
- AI-driven pricing suggestions
- Margin analysis
- Price comparison (current vs suggested)
- Action recommendations (Increase/Decrease/Maintain)
- Reasoning for each recommendation

### 📸 Bill Scanner (OCR)
- Upload bill/receipt images
- Automatic data extraction
- Structured data output
- Item-wise breakdown
- Vendor and date detection

## Technology Stack

- **Frontend**: Pure HTML5, CSS3, JavaScript (ES6+)
- **Design**: Responsive, mobile-friendly
- **API**: RESTful integration with AWS backend
- **Authentication**: JWT-based auth with AWS Cognito
- **Storage**: LocalStorage for session management

## Setup

### 1. Configure API URL

The API URL is already configured in `app.js`:

```javascript
const API_URL = 'https://d2dzik9z94.execute-api.ap-south-1.amazonaws.com/prod';
```

### 2. Open in Browser

Simply open `index.html` in any modern web browser:

```bash
# Windows
start index.html

# Or use a local server
python -m http.server 8000
# Then visit http://localhost:8000
```

### 3. Register/Login

1. Click "Register" tab
2. Fill in your details:
   - Username
   - Password (min 8 characters)
   - Email
   - Phone (+91XXXXXXXXXX)
   - Full Name
   - Shop Name
3. Click "Register"
4. Switch to "Login" tab and login

## Usage Guide

### Adding Inventory Items

1. Go to "Inventory" page
2. Click "+ Add Item"
3. Fill in details:
   - Item ID (unique identifier)
   - Item Name
   - Category
   - Quantity
   - Unit (kg, pcs, ltr)
   - Cost Price
   - Selling Price
   - Min Stock Level
4. Click "Add Item"

### Managing Udhaar

1. Go to "Udhaar" page
2. Click "+ Add Udhaar" to add new credit entry
3. Fill customer details and amount
4. To record payment:
   - Click "Record Payment" on any customer
   - Enter payment amount
   - Click "Record Payment"

### Generating Forecasts

1. Go to "Forecast" page
2. Click "🔄 Generate Forecast"
3. View 7-day predictions for top items
4. Read AI recommendations for stocking

### Getting Pricing Recommendations

1. Go to "Pricing" page
2. Click "🔄 Get Recommendations"
3. View suggested prices for all items
4. See margin improvements and reasoning

### Scanning Bills

1. Go to "Bill Scanner" page
2. Click "Choose File" or drag & drop image
3. Wait for processing
4. View extracted data:
   - Vendor name
   - Date
   - Total amount
   - Item-wise breakdown

## Features Based on Wireframes

### Key Features Implemented
✅ Inventory Management with low stock alerts
✅ Demand Forecasting (7-14 days)
✅ Pricing Recommendations with margin analysis
✅ Udhaar/Credit tracking with payment recording
✅ Bill/Receipt OCR processing
✅ AI-powered recommendations
✅ Real-time alerts and notifications
✅ Dashboard with key metrics

### Process Flow
1. **User Registration** → Create account with shop details
2. **Login** → Authenticate and access dashboard
3. **Add Inventory** → Manually or via OCR
4. **Track Sales** → Monitor inventory levels
5. **Get Forecasts** → AI predicts demand
6. **Optimize Pricing** → AI suggests optimal prices
7. **Manage Udhaar** → Track credit and payments
8. **View Alerts** → Get notified of issues

## Design Highlights

- **Gradient Theme**: Purple-blue gradient matching brand identity
- **Card-based Layout**: Clean, modern card design
- **Responsive**: Works on desktop, tablet, and mobile
- **Intuitive Navigation**: Easy-to-use top navigation
- **Visual Feedback**: Loading states, success/error messages
- **Color-coded Status**: Green (good), Yellow (warning), Red (danger)

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## API Integration

All API calls are handled through helper functions:

```javascript
// GET request
const data = await apiGet('/inventory');

// POST request
const response = await apiPost('/inventory', itemData);
```

Authentication is automatic via JWT token stored in localStorage.

## Troubleshooting

### Login Issues
- Ensure you've registered first
- Check username/password
- Verify API is deployed and accessible

### Data Not Loading
- Check browser console for errors
- Verify JWT token is valid
- Ensure API endpoints are accessible

### OCR Not Working
- Use clear, well-lit images
- Supported formats: JPG, PNG
- Image should contain readable text

## Future Enhancements

- 📱 Progressive Web App (PWA)
- 🔔 Push notifications
- 📊 Advanced analytics charts
- 📤 Export data to Excel/PDF
- 🌐 Multi-language support (Hindi, regional languages)
- 📞 SMS integration for alerts
- 🤖 Chatbot for queries

## Demo Credentials

For testing purposes, register your own account with:
- Username: Your choice
- Password: Min 8 characters (uppercase, lowercase, number)
- Email: Your email address

## Support

For issues or questions:
- Check API documentation: `samaan-sathi/docs/API.md`
- Review troubleshooting guide: `samaan-sathi/docs/TROUBLESHOOTING.md`

---

**Built for Hackathon** - Samaan Sathi AI empowers small retailers with big-company analytics! 🛒✨
