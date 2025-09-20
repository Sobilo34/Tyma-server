# TYMA Backend Service - User Guide

Welcome to the TYMA (The Youth Muslim Association) Backend Service! This guide will help you understand and interact with our backend system, even if you're not a developer.

## 🌟 What is TYMA Backend?

TYMA Backend is the server that powers the TYMA website and mobile applications. Think of it as the brain that handles:

- 📧 **Contact Form Submissions** - When people fill out contact forms on the website
- 📰 **Newsletter Subscriptions** - Managing who wants to receive TYMA updates
- 👥 **Officials Management** - Keeping track of TYMA coordinators and staff
- 🗺️ **Zone Management** - Organizing different geographical areas
- 📝 **News & Events** - Publishing announcements and event information

## 🚀 Quick Start Guide

### For Website Administrators

If you're managing the TYMA website, here's what you need to know:

1. **Contact Forms**: People can submit contact forms through your website
2. **Newsletter**: Visitors can subscribe/unsubscribe from newsletters
3. **Admin Panel**: You can view and manage all submissions through the admin panel

### For Developers Setting Up

If you need to set up the backend service:

## 📋 Setup Instructions

### Prerequisites
- Python 3.8 or higher installed on your computer
- Basic knowledge of using command line/terminal

### Step-by-Step Setup

1. **Download the Code**
   ```bash
   git clone https://github.com/TYMA-Project/server.git
   cd server
   ```

2. **Create a Safe Environment** (Virtual Environment)
   ```bash
   python3 -m venv myvenv
   source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
   ```

3. **Install Required Software**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**
   ```bash
   python manage.py migrate
   ```

5. **Create an Admin Account** (Optional)
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Server**
   ```bash
   python manage.py runserver
   ```

✅ **Success!** Your server is now running at `http://localhost:8000`

---

## 🎯 What Can People Do With Your API?

### 📞 Contact Form Features

**For Website Visitors:**
- Submit contact forms with their questions or feedback
- Choose from different inquiry types (General, Program Info, Volunteer, Donations, Feedback)
- Include their name, email, phone, and message

**For Administrators:**
- View all contact submissions
- Filter by email address or inquiry type
- Mark submissions as responded
- Search through messages

### 📧 Newsletter Features

**For Website Visitors:**
- Subscribe to TYMA newsletter with just their email
- Unsubscribe anytime if they change their mind
- Get confirmation when they subscribe/unsubscribe

**For Administrators:**
- View all newsletter subscribers
- See who's active and who unsubscribed
- Export subscriber lists for email campaigns

### 👥 Officials & Zones Management

**For Administrators:**
- Add new TYMA officials and coordinators
- Organize officials by geographical zones
- Update official information
- Track official positions and roles

---

## 🔗 API Endpoints - How to Use

Think of these as different "doors" on your website where people can submit information or get data:

### 📞 Contact Form Endpoints

#### Submit a Contact Form
- **What it does**: Allows visitors to send messages to TYMA
- **Website URL**: `yourwebsite.com/api/contact/`
- **Required Information**:
  - Name (at least 2 characters)
  - Email address
  - Subject (choose from: GENERAL, PROGRAM, VOLUNTEER, DONATION, FEEDBACK, OTHER)
  - Message (at least 10 characters)
  - Phone number (optional)

#### View Contact Submissions (Admin Only)
- **What it does**: Shows all messages people have sent
- **Admin URL**: `yourwebsite.com/api/contact/`
- **Filter Options**:
  - `email`: Find messages from specific email
  - `subject`: Find messages about specific topics
  - `page`: Navigate through pages of messages
  - `per_page`: How many messages to show per page (max 100)

#### Get Contact Subject Options
- **What it does**: Shows available contact form categories
- **URL**: `yourwebsite.com/api/contact/subjects/`
- **Returns**: List of available subjects like "General Inquiry", "Program Information", etc.

### 📧 Newsletter Endpoints

#### Subscribe to Newsletter
- **What it does**: Adds email to newsletter list
- **Website URL**: `yourwebsite.com/api/newsletter/subscribe/`
- **Required**: Just an email address
- **Features**: 
  - Prevents duplicate subscriptions
  - Reactivates inactive subscriptions automatically

#### Unsubscribe from Newsletter
- **What it does**: Removes email from newsletter list
- **Website URL**: `yourwebsite.com/api/newsletter/unsubscribe/`
- **Required**: Email address to unsubscribe

#### View Newsletter Subscribers (Admin Only)
- **What it does**: Shows who's subscribed to newsletter
- **Admin URL**: `yourwebsite.com/api/newsletter/subscribers/`
- **Filter Options**:
  - `active_only`: Show only active subscribers (default: true)
  - `page`: Navigate through pages
  - `per_page`: How many subscribers to show per page

### 👥 Officials & Zones (Admin Features)

#### Zones Management
- **Create Zone**: `POST /api/zones/` - Add new geographical areas
- **View Zone**: `GET /api/zones/{zone_slug}/` - See zone details
- **List All Zones**: `GET /api/zones/` - View all zones
- **Update Zone**: `PUT /api/zones/{zone_slug}/` - Modify zone information
- **Delete Zone**: `DELETE /api/zones/{zone_slug}/` - Remove zone

#### Officials Management
- **Add Official**: `POST /api/officials/` - Add new TYMA staff/coordinator
- **View Official**: `GET /api/officials/{official_id}/` - See official details
- **List Officials**: `GET /api/officials/` - View all officials with filters
- **Update Official**: `PUT /api/officials/{official_id}/` - Modify official information
- **Delete Official**: `DELETE /api/officials/{official_id}/` - Remove official

---

## 🧪 Testing Your Setup

### Easy Website Testing

**Test Contact Form:**
1. Go to your website's contact page
2. Fill out the form with test information
3. Submit the form
4. Check if you receive confirmation

**Test Newsletter:**
1. Go to newsletter signup on your website
2. Enter a test email address
3. Check if subscription confirmation appears

### Technical Testing (For Developers)

We've included a test script to verify everything works:

```bash
# Run the test script
python test_endpoints.py
```

This will automatically test:
- ✅ Contact form submission (valid and invalid)
- ✅ Newsletter subscription (valid and invalid emails)
- ✅ Getting contact subject options
- ✅ Error handling

---

## 🎨 Integration Examples

### For Website Developers

**HTML Contact Form Example:**
```html
<form id="contact-form">
    <input type="text" name="name" placeholder="Your Name" required>
    <input type="email" name="email" placeholder="Your Email" required>
    <select name="subject" required>
        <option value="GENERAL">General Inquiry</option>
        <option value="PROGRAM">Program Information</option>
        <option value="VOLUNTEER">Volunteer Opportunity</option>
        <option value="DONATION">Donation Question</option>
        <option value="FEEDBACK">Feedback/Suggestion</option>
        <option value="OTHER">Other</option>
    </select>
    <input type="tel" name="phone" placeholder="Phone (optional)">
    <textarea name="message" placeholder="Your Message" required></textarea>
    <button type="submit">Send Message</button>
</form>
```

**JavaScript Newsletter Signup:**
```javascript
// Newsletter subscription
function subscribeNewsletter(email) {
    fetch('/api/newsletter/subscribe/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email: email})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Successfully subscribed to newsletter!');
        } else {
            alert('Error: ' + data.message);
        }
    });
}
```---

## Running the Service

Start the development server:
```bash
python manage.py runserver
```
The API will be available at `http://localhost:8000/`.

---

## API Endpoints

Below are the main endpoints. You can use tools like [Postman](https://www.postman.com/) or `curl` to interact with them.

### Zones

- **Create Zone**
	- `POST /api/zones/`
	- Body: `{ "name": "North Zone", "description": "Covers northern region" }`

- **Get Zone by ID**
	- `GET /api/zones/{zone_id}/`

- **Get All Zones**
	- `GET /api/zones/`

### News

- **Create News**
	- `POST /api/news/`
	- Body: `{ "title": "Event Update", "content": "Details...", "category_id": 1 }`

- **Get News by ID**
	- `GET /api/news/{news_id}/`

- **Get All News**
	- `GET /api/news/?news_type=update&category_id=1&is_featured=true&limit=10`

### Camps

- **Create Camp**
	- `POST /api/camps/`
	- Body: `{ "name": "Summer Camp", "location": "City Park", "start_date": "2025-06-01" }`

- **Get Camp by ID**
	- `GET /api/camps/{camp_id}/`

- **Get All Camps**
	- `GET /api/camps/`

### Officials

- **Create Official**
  - `POST /api/officials/`
  - Body: `{ "name": "John Doe", "zone": 1, "official_type": "Coordinator" }`

- **Get Official by ID**
  - `GET /api/officials/{official_id}/`

- **Get All Officials**
  - `GET /api/officials/`

### Contact Us

- **Submit Contact Form**
  - `POST /api/contact/`
  - Body: `{ "name": "John Doe", "email": "john@example.com", "subject": "GENERAL", "message": "Hello..." }`

- **Get Contact Submissions (Admin)**
  - `GET /api/contact/`
  - Query Parameters:
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 10)
    - `email`: Filter by email (partial match)
    - `subject`: Filter by subject (exact match - use values like GENERAL, PROGRAM, VOLUNTEER, DONATION, FEEDBACK, OTHER)

- **Get Available Contact Subjects**
  - `GET /api/contact/subjects/`

### Newsletter

- **Subscribe to Newsletter**
  - `POST /api/newsletter/subscribe/`
  - Body: `{ "email": "user@example.com" }`

- **Unsubscribe from Newsletter**
  - `POST /api/newsletter/unsubscribe/`
  - Body: `{ "email": "user@example.com" }`

- **Get Newsletter Subscribers (Admin)**
  - `GET /api/newsletter/subscribers/`
  - Query Parameters:
    - `page`: Page number (default: 1)
    - `per_page`: Items per page (default: 10)
    - `active_only`: Filter only active subscribers (default: true)---

## Testing Endpoints

You can test endpoints using `curl` or Postman.

### Example: Submit Contact Form

```bash
curl -X POST http://localhost:8000/api/contact/ \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john@example.com",
       "subject": "GENERAL",
       "message": "I would like to know more about TYMA programs."
     }'
```

### Example: Subscribe to Newsletter

```bash
curl -X POST http://localhost:8000/api/newsletter/subscribe/ \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com"}'
```

### Example: Get Contact Submissions with Filters

```bash
# Get all contact submissions for a specific email
curl "http://localhost:8000/api/contact/?email=john@example.com"

# Get all contact submissions with subject "GENERAL"
curl "http://localhost:8000/api/contact/?subject=GENERAL"

# Get contact submissions with both email and subject filters
curl "http://localhost:8000/api/contact/?email=john&subject=VOLUNTEER&page=1&per_page=5"
```

### Example: Get Available Contact Subjects

```bash
curl http://localhost:8000/api/contact/subjects/
```---

## 🛠️ Troubleshooting Common Issues

### "I can't connect to the database"

**Problem**: Error messages about database connections

**Solutions**:
1. Make sure you've run: `python manage.py migrate`
2. Check if `db.sqlite3` file exists in your project folder
3. Try running: `python manage.py makemigrations` then `python manage.py migrate`

### "Email not being saved"

**Problem**: Newsletter signups or contact forms not working

**Solutions**:
1. Check if email address is valid (contains @ and domain)
2. For contact forms, make sure message is at least 10 characters
3. Check the browser's developer tools for error messages

### "Page not found" errors

**Problem**: URLs not working

**Solutions**:
1. Make sure the server is running: `python manage.py runserver`
2. Check the URL - should start with `http://localhost:8000/api/`
3. Verify your URL patterns in `urls.py`

### "Permission denied" for admin features

**Problem**: Can't access admin-only features

**Solutions**:
1. Create admin account: `python manage.py createsuperuser`
2. Login through Django admin at `http://localhost:8000/admin/`
3. Make sure you're logged in when accessing admin endpoints

### Database migration errors

**Problem**: Errors when running migrations

**Solutions**:
1. Try: `python manage.py makemigrations home`
2. Then: `python manage.py migrate`
3. If still failing, check for conflicting migrations in `home/migrations/`

---

## 📚 Technical Details (For Developers)

### Security Features
- **Input Validation**: All forms validate data before saving
- **XSS Prevention**: User input is sanitized to prevent attacks
- **Database Indexes**: Optimized for fast queries
- **Email Validation**: Prevents invalid email addresses
- **Rate Limiting Ready**: Structure supports rate limiting implementation

### Database Schema

**ContactSubmission Model:**
- `name`: User's full name (max 100 chars)
- `email`: Valid email address (max 254 chars, indexed)
- `phone`: Optional phone number (max 20 chars)
- `subject`: Category (GENERAL, PROGRAM, VOLUNTEER, DONATION, FEEDBACK, OTHER)
- `message`: Contact message (min 10 chars, max 1000 chars)
- `created_at`: Timestamp (indexed for fast queries)

**NewsletterSubscriber Model:**
- `email`: Unique email address (indexed)
- `is_active`: Whether subscription is active
- `subscribed_at`: When user subscribed
- `unsubscribed_at`: When user unsubscribed (if applicable)

### API Response Format

All endpoints return consistent JSON format:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { /* response data */ }
}
```

Error responses:
```json
{
  "success": false,
  "message": "Error description",
  "errors": { /* detailed error info */ }
}
```

---

## 🚀 Advanced Configuration

### Environment Variables
Create a `.env` file for production settings:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Production Deployment
1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Use HTTPS for all communications
5. Configure email backend for contact form notifications

### Database Optimization
- Contact submissions are indexed by email and creation date
- Newsletter subscriptions are indexed by email
- Pagination is implemented for large datasets
- Query optimization for admin views

---

## 📝 Changelog

### Recent Updates
- ✅ Added comprehensive contact form API with subject categorization
- ✅ Implemented newsletter subscription/unsubscription system  
- ✅ Enhanced input validation and security measures
- ✅ Added pagination for admin views
- ✅ Implemented HTML sanitization for XSS prevention
- ✅ Added database indexing for performance
- ✅ Created comprehensive error handling
- ✅ Added admin filtering and search capabilities

### Coming Soon
- 📧 Email notification system for contact form submissions
- 🔄 Automated newsletter sending functionality
- 📊 Analytics dashboard for contact and newsletter metrics
- 🔒 API rate limiting implementation
- 📱 Mobile app API endpoints

---

## 🤝 Support & Contributing

### Getting Help
1. Check this README first
2. Look for similar issues in the troubleshooting section
3. Test with the provided `test_endpoints.py` script
4. Check Django logs for error details

### For Developers
- Follow Django best practices
- Write tests for new features
- Update documentation when adding features
- Use proper commit messages

### Contact
For technical support or questions about TYMA backend development, please use the contact form functionality or reach out through official TYMA channels.

---

*TYMA Backend - Building better communities through technology* 🌟

---

## Additional Notes

- All endpoints return JSON responses.
- Authentication may be required for some endpoints (see API documentation if available).
- For more details, check the source code in the `home/views.py` and related service files.

---

Feel free to ask for more specific examples or details about any endpoint!


