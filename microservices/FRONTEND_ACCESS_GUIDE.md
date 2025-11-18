# 🌐 Frontend Access Guide

## YES! You Have a Full Frontend Web Interface

Your microservices architecture includes a **complete web interface** served by the Frontend Gateway on port 5000.

---

## 🚀 How to Access

Simply open your web browser and navigate to:

### **http://localhost:5000**

---

## 📱 Available Pages

### 1. **Homepage**
**URL:** http://localhost:5000

This is your landing page with:
- NexTurn branding and logo
- Navigation menu
- Overview of the queue management system
- Links to signup/login

---

### 2. **Signup Page**
**URL:** http://localhost:5000/signup

Create a new user account with:
- Full Name
- Email
- Organization (optional)
- Password
- Confirm Password

**After signup:** You'll be redirected to the login page

---

### 3. **Login Page**
**URL:** http://localhost:5000/login

Login with your credentials:
- Email
- Password

**After login:** You'll receive a JWT token and can access protected pages

---

### 4. **Businesses List**
**URL:** http://localhost:5000/businesses

Browse all registered businesses:
- View business names, categories, and addresses
- Click on a business to see its queues
- Join queues as a customer

---

### 5. **Register Business**
**URL:** http://localhost:5000/register-business

**(Requires login)** Create your own business:
- Business Name
- Category (Restaurant, Cafe, Bank, etc.)
- Address
- Phone Number
- Description

**Note:** A default queue is automatically created when you register a business!

---

### 6. **Business Dashboard**
**URL:** http://localhost:5000/business-dashboard

**(Requires login)** Manage your business:
- View your registered businesses
- See queue statistics
- Manage queues
- View customers waiting

---

### 7. **Business Queues**
**URL:** http://localhost:5000/business-queues

View and manage queues for your business:
- See all queues for your business
- Create new queues
- Edit queue settings
- See current queue size

---

### 8. **Manage Queue**
**URL:** http://localhost:5000/manage-queue

Control a specific queue:
- See all customers in line
- Serve next customer
- View wait times
- Manage queue status (active/paused)

---

### 9. **Ticket Page**
**URL:** http://localhost:5000/ticket

View your ticket after joining a queue:
- Ticket ID (UUID)
- Your position in queue
- Estimated wait time
- Business information
- Leave queue button

---

### 10. **Queue History**
**URL:** http://localhost:5000/queue-history

View your past queue experiences:
- Previous tickets
- Businesses you've visited
- Wait times experienced
- Feedback given

---

### 11. **Feedback Form**
**URL:** http://localhost:5000/feedback-form

Submit feedback about your experience:
- Rating (1-5 stars)
- Comments
- Service quality

---

## 🎨 What You Should See

The frontend includes:

✅ **Professional Design** with Tailwind CSS
✅ **Responsive Layout** works on desktop and mobile
✅ **NexTurn Logo** and branding
✅ **Navigation Menu** to switch between pages
✅ **Form Validation** for user inputs
✅ **Real-time Updates** when joining/leaving queues
✅ **Toast Notifications** for success/error messages

---

## 🔧 Frontend Architecture

```
┌─────────────────────────────────────┐
│         Browser (You)               │
│                                     │
│   http://localhost:5000             │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Frontend Gateway Service          │
│   (Port 5000)                       │
│                                     │
│   - Serves HTML Templates           │
│   - Serves Static Files (CSS/JS)   │
│   - Routes API Requests             │
│   - Manages Sessions & JWT          │
└─────────────┬───────────────────────┘
              │
              ├──────────┬──────────┬──────────┐
              ▼          ▼          ▼          ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │  Auth   │ │Business │ │ Queue   │
        │ Service │ │ Service │ │ Service │
        │ (5001)  │ │ (5002)  │ │ (5003)  │
        └─────────┘ └─────────┘ └─────────┘
```

---

## 🧪 Try It Out!

### Step 1: Open the Homepage
1. Open browser
2. Go to http://localhost:5000
3. You should see the NexTurn homepage

### Step 2: Create an Account
1. Click "Sign Up" or go to http://localhost:5000/signup
2. Fill in the form:
   - Full Name: `Your Name`
   - Email: `youremail@example.com`
   - Password: `password123`
   - Confirm Password: `password123`
3. Click "Create Account"
4. You'll be redirected to login

### Step 3: Login
1. Go to http://localhost:5000/login
2. Enter your email and password
3. Click "Log In"
4. You're now logged in!

### Step 4: Browse Businesses
1. Go to http://localhost:5000/businesses
2. You'll see a list of businesses
3. Click on any business to see its queues

### Step 5: Register Your Own Business
1. Go to http://localhost:5000/register-business
2. Fill in business details:
   - Name: `My Coffee Shop`
   - Category: `Cafe`
   - Address: `123 Main Street`
   - Phone: `555-0100`
3. Click "Register Business"
4. A default queue is created automatically!

### Step 6: Manage Your Business
1. Go to http://localhost:5000/business-dashboard
2. See your business statistics
3. Click on "Manage Queues"
4. Serve customers when they join your queue

---

## 🖼️ Screenshots Guide

When you open http://localhost:5000, you should see:

### Homepage Features:
- **Header:** NexTurn logo and navigation menu
- **Hero Section:** Welcome message and call-to-action buttons
- **Features Section:** Overview of what NexTurn offers
- **Footer:** Links and information

### Login/Signup Pages:
- Clean, modern forms
- Input validation
- Password strength indicators
- Links to switch between login/signup

### Business Pages:
- Grid layout showing businesses
- Cards with business information
- Queue status indicators
- Join/manage buttons

---

## 📂 Files Serving the Frontend

### HTML Templates (in `/templates/`)
- `index.html` - Homepage
- `login.html` - Login page
- `signup.html` - Signup page
- `businesses_list.html` - Browse businesses
- `register_business.html` - Register new business
- `business_dashboard.html` - Business owner dashboard
- `business_queues.html` - Queue management
- `manage_queue.html` - Single queue management
- `ticket.html` - Customer ticket view
- `queue_history.html` - Past tickets
- `feedback_form.html` - Submit feedback
- `feedback_list.html` - View feedback

### Static Files (in `/static/`)
- `logo.png` - NexTurn logo
- `style.css` - Custom styles
- `api-config.js` - JavaScript utilities for API calls

---

## 🔗 Direct Links (Click to Open)

Open these URLs in your browser:

**Main Pages:**
- Homepage: http://localhost:5000
- Login: http://localhost:5000/login
- Signup: http://localhost:5000/signup

**Customer Pages:**
- Browse Businesses: http://localhost:5000/businesses
- My Ticket: http://localhost:5000/ticket
- Queue History: http://localhost:5000/queue-history

**Business Owner Pages:**
- Register Business: http://localhost:5000/register-business
- My Dashboard: http://localhost:5000/business-dashboard
- My Queues: http://localhost:5000/business-queues
- Manage Queue: http://localhost:5000/manage-queue

**Feedback:**
- Submit Feedback: http://localhost:5000/feedback-form
- View Feedback: http://localhost:5000/feedback-list

---

## 🐛 Troubleshooting

### "Can't Access http://localhost:5000"

**Check if frontend service is running:**
```bash
cd NexTurn/microservices
docker-compose ps frontend-service
```

Should show `Up` status.

**Restart frontend service:**
```bash
docker-compose restart frontend-service
```

---

### "Page Loads but No Styling"

**Check if static files are accessible:**
- Open http://localhost:5000/static/logo.png
- You should see the NexTurn logo

**If not loading:**
```bash
docker-compose logs frontend-service | grep "static"
```

---

### "Forms Don't Submit"

**Check JavaScript console in browser:**
1. Press F12 to open Developer Tools
2. Go to "Console" tab
3. Look for errors

**Common issues:**
- JWT token expired: Login again
- CORS errors: Already configured, shouldn't happen
- Network errors: Check if backend services are running

---

## 💡 Pro Tips

### Use Multiple Browser Windows
1. **Window 1:** Login as business owner
2. **Window 2 (Incognito):** Login as customer
3. Test the full flow: customer joins queue, owner serves them

### Check Network Tab
1. Press F12 in browser
2. Go to "Network" tab
3. See all API calls being made
4. Verify requests to backend services

### Test Different User Roles
1. Create business owner account
2. Create customer account
3. Test permissions and access control

---

## ✅ What Should Work

When you access http://localhost:5000:

✅ Homepage loads with NexTurn branding
✅ Can navigate to signup/login pages
✅ Can create a new account (signup)
✅ Can login and receive JWT token
✅ Can browse businesses without login
✅ Can register a business (requires login)
✅ Can view business dashboard (requires login)
✅ Can join queues (requires login)
✅ Can leave queues
✅ Can submit feedback
✅ Forms validate input
✅ Toast notifications appear

---

## 🎉 Summary

**YES!** You have a complete, functional frontend web interface at:

# **http://localhost:5000**

It includes:
- 12 different pages
- Professional styling with Tailwind CSS
- Form validation
- Real-time updates
- JWT authentication
- Session management
- API integration with all microservices

**Just open your browser and start using it!** 🚀

---

## 📞 Need Help?

If you're still not seeing the frontend:

1. **Check service status:**
   ```bash
   cd NexTurn/microservices
   docker-compose ps
   ```

2. **Check logs:**
   ```bash
   docker-compose logs frontend-service
   ```

3. **Restart everything:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Access directly:**
   Open browser → http://localhost:5000

The frontend is working - you just need to open it in your browser! 🌐
