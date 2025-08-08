# NeelamPal - An Online Auction Portal

NeelamPal is a modern, retro-themed online auction platform built with Django. It connects organizations and bidders, enabling seamless item listings, bidding, and auction management in a secure and transparent environment.

## Features

- **Organization & Bidder Accounts:** Separate registration and login flows for organizations and bidders.
- **Item Listings:** Organizations can list items for auction with images, descriptions, and starting bids.
- **Live Bidding:** Bidders can place real-time bids and track auction progress.
- **Profile Management:** Edit and update user profiles.
- **Retro Black & White UI:** Minimal, blocky, and accessible design inspired by classic web interfaces.
- **Responsive Design:** Works smoothly on desktops and mobile devices.
- **Secure Authentication:** Built-in Django authentication and password management.
- **Admin Controls:** Manage users, items, and auctions from the Django admin panel.

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)
- [Cloudinary](https://cloudinary.com/) account for image uploads (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/NeelamPal-An-Online-Auction-Portal.git
   cd NeelamPal-An-Online-Auction-Portal
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your secret keys and Cloudinary credentials.

5. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

9. **Access the site:**
   - Open [http://localhost:8000](http://localhost:8000) in your browser.

## Folder Structure

```
NeelamPal-An-Online-Auction-Portal/
├── Auction/
│   ├── static/
│   │   └── Auction/
│   │       ├── css/
│   │       │   └── app.css
│   │       └── js/
│   │           └── app.js
│   ├── templates/
│   │   └── Auction/
│   │       ├── layout.html
│   │       └── index.html
│   ├── views.py
│   └── ...
├── manage.py
└── requirements.txt
```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

---

**NeelamPal** – Simple, secure, and retro auctions for everyone.