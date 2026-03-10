# App Context for Test Generation

**App Name:** YourApp  
**Type:** [e.g., E-commerce, Social Media, Finance, etc.]  
**Target Platform:** iOS

---

## Overview

Brief description of what the app does (2-3 sentences).

Example:
- A shopping app where users browse items, add to cart, and checkout
- Users must login to access most features
- Items are organized by categories and have search functionality

---

## Main Features

1. **Authentication**
   - Login with email/password
   - Logout from profile screen
   
2. **Item Browsing**
   - List of items on main screen
   - Each item shows: title, price, category, image
   - Items can be filtered by category
   - Search functionality
   
3. **Item Details**
   - Tap item to see full details
   - Can add to favorites
   - View related items
   
4. **Profile**
   - User info display
   - Settings
   - Logout button

---

## User Flows

### Login Flow
1. Launch app → Login screen
2. Enter email + password
3. Tap login → Items list appears

### Browse Items Flow
1. After login → Items list screen
2. Scroll through items
3. Tap item → Details screen
4. Back button returns to list

### Tab Navigation
- Items tab (default)
- Profile tab
- Settings tab

---

## Common Test Scenarios

- **Happy path:** Login → Browse items → View details → Logout
- **Error:** Login with invalid credentials → Error message shown
- **Navigation:** Switch between tabs
- **Search:** Enter search term → Filtered results
- **Data validation:** Empty fields → Validation errors

---

## Technical Notes

- Default credentials: test@example.com / password123
- Items are dynamically loaded
- Uses SwiftUI navigation
- Tab bar navigation pattern
