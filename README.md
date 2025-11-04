# NexTurn Testing Guide

## Setup

It is recommended to use a virtual environment for dependencies.

- To create and activate a virtual environment, run:
  ```bash
  python -m venv venv
  # On Windows:
  venv\Scripts\activate
  # On Mac/Linux:
  source venv/bin/activate
  ```
- Then, install all required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Start the Application

```bash
cd path/to/NexTurn
python app.py
```

Then open your browser to: **http://127.0.0.1:5000**

---

## Test Scenario 1: Customer Journey

### 1. Sign Up as a Customer

1. Navigate to http://127.0.0.1:5000
2. Click "Sign up" on the login page
3. Fill in the form:
   - Full Name: `John Doe`
   - Email: `john@test.com`
   - Password: `password123`
   - Confirm Password: `password123`
   - Organization: (leave blank or enter anything)
4. Click "Create account"
5. **Expected Result**: Redirected to login page with success message

### 2. Login as Customer

1. Enter credentials:
   - Email: `john@test.com`
   - Password: `password123`
2. Click "Log In"
3. **Expected Result**: Redirected to home page, user is logged in

### 3. Browse Businesses (Initial State)

1. Click "Browse Businesses" in the navbar
2. **Expected Result**: Message "No businesses available yet"

---

## Test Scenario 2: Business Owner Journey

### 1. Sign Up as Business Owner

1. Open an **incognito/private browser window**
2. Go to http://127.0.0.1:5000
3. Click "Sign up"
4. Fill in the form:
   - Full Name: `Jane Business Owner`
   - Email: `jane@business.com`
   - Password: `business123`
   - Confirm Password: `business123`
   - Organization: `My Restaurant`
5. Click "Create account"
6. Login with the new credentials
7. **Expected Result**: Successfully logged in

### 2. Register a Business

1. Click "Business Dashboard" in the navbar
2. Click "Register New Business" button
3. Fill in the form:
   - Business Name: `Joe's Café`
   - Category: `Café`
   - Description: `Best coffee in town!`
   - Address: `123 Main Street, City`
4. Click "Register Business"
5. **Expected Result**:
   - Success message displayed
   - Redirected to Business Dashboard
   - Business "Joe's Café" is listed
   - Shows "1 active queue(s)"

### 3. View Business Dashboard

1. On the Business Dashboard page
2. **Expected Result**:
   - Your business "Joe's Café" is displayed
   - Shows category, address
   - Lists "Main Queue" (automatically created)
   - "View Customer Feedback" button is visible

### 4. Manage a Queue

1. Click "Main Queue" under your business
2. **Expected Result**:
   - Page shows queue management interface
   - Analytics section displays:
     - Total Customers Served: 0
     - Average Wait Time: 0 min
     - Current Queue Size: 0
   - Active Queue section shows "No customers in queue"
   - Page has auto-refresh notice (every 30 seconds)

---

## Test Scenario 3: Customer Joins Queue

### 1. Browse Businesses as Customer

1. Switch back to customer browser window (john@test.com)
2. Navigate to http://127.0.0.1:5000/businesses
3. **Expected Result**: "Joe's Café" is now listed

### 2. View Business Queues

1. Click "View Queues" on Joe's Café
2. **Expected Result**:
   - Business details displayed (name, category, address)
   - "Leave Feedback" button visible
   - "Main Queue" shown with:
     - Current queue size: 0 people
     - Average service time: 5 minutes
     - Estimated wait time: ~0 minutes
   - "Join Queue" button available

### 3. Join a Queue

1. Click "Join Queue" button
2. **Expected Result**:
   - Redirected to ticket page
   - Ticket displays:
     - Unique Ticket ID
     - Position: #1
     - Estimated Wait Time: 0 minutes
   - "Back to Home" and "Leave Queue" buttons visible
   - Alert Settings section displayed

---

## Test Scenario 4: Business Serves Customer

### 1. View Customer in Queue

1. Switch to business owner window (jane@business.com)
2. Navigate to Business Dashboard → Joe's Café → Main Queue
3. **Expected Result**:
   - Current Queue Size: 1
   - Table shows customer details:
     - Position: #1 (highlighted in green)
     - Customer: John Doe
     - Email: john@test.com
     - Joined At: (timestamp)
     - Ticket ID: (partial ID shown)
   - "Serve Next Customer" button is enabled

### 2. Serve the Customer

1. Click "Serve Next Customer" button
2. **Expected Result**:
   - Success message: "Next customer served successfully!"
   - Customer removed from active queue
   - Current Queue Size: 0
   - Analytics updated:
     - Total Customers Served: 1
     - Average Wait Time: (calculated value)

---

## Test Scenario 5: Queue History

### 1. View Personal Queue History

1. Switch to customer window (john@test.com)
2. Click "My History" in the navbar
3. **Expected Result**:
   - Table displays queue history
   - Shows recent entry:
     - Business: Joe's Café
     - Queue: Main Queue
     - Position: #1
     - Status: Completed (green badge)
     - Wait Time: (calculated in minutes)
     - Joined timestamp

---

## Test Scenario 6: Multiple Customers in Queue

### 1. Create Additional Customer Accounts

1. Open 3 new incognito windows
2. Create accounts:
   - Email: `alice@test.com`, Password: `password123`
   - Email: `bob@test.com`, Password: `password123`
   - Email: `charlie@test.com`, Password: `password123`

### 2. Have Multiple Customers Join Queue

1. For each customer account:
   - Navigate to Browse Businesses → Joe's Café → View Queues
   - Click "Join Queue"
2. **Expected Result**:
   - Alice gets Position #1
   - Bob gets Position #2
   - Charlie gets Position #3

### 3. View Queue as Business Owner

1. Switch to business owner window
2. Go to Business Dashboard → Main Queue
3. **Expected Result**:
   - Current Queue Size: 3
   - Table shows all 3 customers
   - First customer (Alice, position #1) highlighted in green
   - Customers listed in order: Alice, Bob, Charlie

### 4. Serve Multiple Customers

1. Click "Serve Next Customer" 3 times (once for each customer)
2. After each click, **Expected Result**:
   - Success message displayed
   - Served customer removed from queue
   - Remaining customers move up in position
   - Analytics update (Total Served increases, Average Wait Time calculated)

---

## Test Scenario 7: Leave Queue Functionality

### 1. Join Queue and Leave

1. As a customer (any account)
2. Join Joe's Café → Main Queue
3. Ensure you're NOT at position #1 (have another customer join first)
4. On your ticket page, click "Leave Queue"
5. Confirm the action
6. **Expected Result**:
   - Confirmation dialog appears
   - After confirming, redirected to home page
   - Success message: "You have left the queue successfully"

### 2. Verify Queue Leave

1. Check "My History"
2. **Expected Result**: Most recent entry shows Status: Cancelled (red badge)

3. As business owner, check the queue
4. **Expected Result**: Customer no longer appears in active queue

---

## Test Scenario 8: Customer Feedback System

### 1. Submit Feedback

1. As customer (john@test.com)
2. Navigate to Browse Businesses → Joe's Café → View Queues
3. Click "Leave Feedback" button
4. Fill in the form:
   - Rating: Click on `5` (1-5 scale)
   - Comments: `Great service, loved the coffee!`
5. Click "Submit Feedback"
6. **Expected Result**:
   - Success message: "Thank you for your feedback!"
   - Redirected to businesses list

### 2. Submit More Feedback (Different Ratings)

1. Create/use different customer accounts
2. Submit feedback with various ratings:
   - alice@test.com: Rating 4, Comment: "Good atmosphere"
   - bob@test.com: Rating 5, Comment: "Excellent!"
   - charlie@test.com: Rating 3, Comment: "Average experience"

### 3. View Feedback as Business Owner

1. Switch to business owner (jane@business.com)
2. Go to Business Dashboard
3. Click "View Customer Feedback" under Joe's Café
4. **Expected Result**:
   - Average Rating displayed prominently (e.g., 4.3)
   - Shows "Based on 4 review(s)"
   - List of all feedback entries showing:
     - Customer names
     - Star ratings (visual)
     - Comments
     - Timestamps

---

## Test Scenario 9: Alert Settings

### 1. Configure Alerts

1. As customer in queue (any account)
2. Navigate to your ticket page
3. Scroll to "Alert Settings" section
4. Configure:
   - Check "Enable Alerts" checkbox
   - Check both "Browser Notification" and "Email"
   - Select Alert Threshold: "Position ≤ 3"
5. Click "Save Alert Preferences"
6. **Expected Result**:
   - Success message: "Alert preferences updated successfully"
   - Green confirmation box appears: "Alert scheduled: when position ≤ 3"

### 2. Verify Alert Settings Persist

1. Refresh the ticket page
2. **Expected Result**:
   - Alert settings remain as configured
   - "Enable Alerts" is still checked
   - Both notification channels are selected
   - Threshold shows "Position ≤ 3"

---

## Test Scenario 10: Multiple Queues per Business

### 1. Add Additional Queues (Manual Setup)

1. Stop the Flask server (Ctrl+C)
2. Open Python shell:

```bash
python
```

3. Run this code:

```python
import sqlite3
conn = sqlite3.connect('users.db')
cur = conn.cursor()

# Get business ID
cur.execute("SELECT id FROM businesses WHERE name = 'Joe''s Café'")
business_id = cur.fetchone()[0]

# Add VIP Queue
cur.execute("""
    INSERT INTO queues (business_id, name, avg_service_time, is_active)
    VALUES (?, 'VIP Queue', 3, 1)
""", (business_id,))

# Add Takeout Queue
cur.execute("""
    INSERT INTO queues (business_id, name, avg_service_time, is_active)
    VALUES (?, 'Takeout Queue', 2, 1)
""", (business_id,))

conn.commit()
conn.close()
exit()
```

4. Restart Flask server:

```bash
python app.py
```

### 2. Test Multiple Queues as Business Owner

1. Login as jane@business.com
2. Go to Business Dashboard
3. **Expected Result**:
   - Joe's Café now shows "3 active queue(s)"
   - Lists: Main Queue, VIP Queue, Takeout Queue
   - Each queue is clickable

### 3. Test Multiple Queues as Customer

1. Login as john@test.com
2. Navigate to Browse Businesses → Joe's Café → View Queues
3. **Expected Result**:
   - All 3 queues displayed
   - Each shows:
     - Different average service times (5 min, 3 min, 2 min)
     - Current queue size
     - Estimated wait time
   - Can join any queue

### 4. Join Different Queues

1. With different customer accounts, join different queues:
   - Alice → Main Queue
   - Bob → VIP Queue
   - Charlie → Takeout Queue
2. As business owner, manage each queue separately
3. **Expected Result**:
   - Each queue manages customers independently
   - Serving a customer in one queue doesn't affect others

---

## Test Scenario 11: Edge Cases and Error Handling

### 1. Test Duplicate Email Registration

1. Try to sign up with an existing email (e.g., john@test.com)
2. **Expected Result**: Error message: "Email already registered"

### 2. Test Password Mismatch

1. During signup, enter different passwords in Password and Confirm Password
2. **Expected Result**: Error message: "Passwords do not match"

### 3. Test Invalid Login

1. Try to login with wrong password
2. **Expected Result**: Error message: "The email or password is incorrect"

### 4. Test Joining Queue While Already in Queue

1. Join a queue as a customer
2. Try to join another queue (or same queue again)
3. **Expected Result**: Error message: "You are already in a queue. Leave your current queue first."

### 5. Test Accessing Business Dashboard Without Business

1. Login as regular customer (john@test.com)
2. Navigate to /business/dashboard
3. **Expected Result**: Shows "You haven't registered any businesses yet"

### 6. Test Unauthorized Access

1. As customer (john@test.com), try to access:
   - /business/1/queue/1 (another business's queue)
2. **Expected Result**: Error message: "Unauthorized access" and redirect

---

## Test Scenario 12: UI/UX Testing

### 1. Test Responsive Design

1. Resize browser window to mobile size (375px width)
2. Navigate through all pages
3. **Expected Result**: All pages are readable and functional on mobile

### 2. Test Navigation Flow

1. From home page, navigate through:
   - Browse Businesses → Business Queues → Join Queue → Ticket
   - My History
   - Business Dashboard → Manage Queue
2. **Expected Result**: All links work, navigation is intuitive

### 3. Test Auto-Refresh

1. As business owner, open Manage Queue page
2. As customer (in different window), join the queue
3. Wait 30 seconds on business owner's page
4. **Expected Result**: Page auto-refreshes and shows new customer

### 4. Test Flash Messages

1. Perform various actions (join queue, leave queue, register business, submit feedback)
2. **Expected Result**:
   - Success messages appear in green
   - Error messages appear in red
   - Messages are clear and descriptive

---

## Test Scenario 13: Data Persistence

### 1. Test Database Persistence

1. Perform several actions:
   - Register business
   - Join queue
   - Submit feedback
2. Stop the Flask server (Ctrl+C)
3. Restart the server: `python app.py`
4. Login and check:
   - Business still exists
   - Queue history persists
   - Feedback is still there
5. **Expected Result**: All data persists after server restart

---

## Quick Testing Checklist

Use this checklist for rapid testing:

- [ ] User signup works
- [ ] User login works
- [ ] User logout works
- [ ] Business registration works
- [ ] Business dashboard displays correctly
- [ ] Can browse all businesses
- [ ] Can view business queues
- [ ] Can join a queue
- [ ] Ticket page displays position and ETA
- [ ] Can leave a queue
- [ ] Business can view active queue
- [ ] Business can serve next customer
- [ ] Queue positions update correctly
- [ ] Analytics update after serving customers
- [ ] Queue history tracks all activities
- [ ] Can submit feedback with rating
- [ ] Can view business feedback
- [ ] Average rating calculates correctly
- [ ] Alert settings save properly
- [ ] Multiple queues work independently
- [ ] Flash messages display correctly
- [ ] Unauthorized access is blocked
- [ ] Data persists after restart

---

## Performance Testing

### Test with High Load

1. Create 20+ customer accounts
2. Have all join the same queue
3. As business owner, serve them one by one
4. **Expected Result**:
   - Page remains responsive
   - Analytics calculate correctly
   - No lag in position updates

---

## Known Issues to Watch For

While testing, watch for these potential issues:

1. **In-memory queue vs database**: The app uses both in-memory Queue object and database. Ensure they stay in sync.
2. **Session management**: Ticket ID stored in session - clearing cookies will lose active ticket.
3. **Auto-refresh timing**: Page refreshes every 30 seconds - manual refresh needed for immediate updates.
4. **Leave queue**: Ensure database is updated when leaving queue.

---

## Test Data Summary

### Test Accounts Created

- **Customers:**

  - john@test.com / password123
  - alice@test.com / password123
  - bob@test.com / password123
  - charlie@test.com / password123

- **Business Owner:**
  - jane@business.com / business123

### Test Businesses

- Joe's Café (Category: Café)
  - Main Queue (5 min service time)
  - VIP Queue (3 min service time) - _if added manually_
  - Takeout Queue (2 min service time) - _if added manually_

---

## Troubleshooting

### If Flask won't start:

```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill the process if needed, then restart
python app.py
```

### If database errors occur:

```bash
# Delete and recreate database
rm users.db
python app.py
# Database will be recreated on startup
```

### If styles don't load:

- Hard refresh browser: Ctrl+F5
- Check browser console for errors
- Verify Tailwind CDN is accessible

---

## Success Criteria

All tests pass if:

1. ✅ All user flows complete without errors
2. ✅ Data persists correctly in database
3. ✅ UI is responsive and user-friendly
4. ✅ Analytics calculate accurately
5. ✅ Authorization prevents unauthorized access
6. ✅ Flash messages provide clear feedback
7. ✅ Multi-queue functionality works correctly
8. ✅ Feedback system displays ratings properly

---

## Report Issues

If you find bugs during testing, document:

1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Browser and OS version
5. Screenshots if applicable

---

**Testing completed on:** ******\_******

**Tested by:** ******\_******

**Overall Status:** [ ] Pass [ ] Fail

**Notes:**
